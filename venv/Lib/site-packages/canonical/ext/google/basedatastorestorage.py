# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import contextlib
import functools
import inspect
from typing import cast
from typing import Any
from typing import AsyncIterable
from typing import Callable
from typing import Iterable
from typing import Mapping
from typing import TypeVar

import pydantic
from google.cloud.datastore import Client

from canonical import PersistedModel
from canonical import ResourceIdentifier
from canonical.protocols import ITransaction
from canonical.utils import class_property
from canonical.utils import merge_signatures
from .datastorecursor import DatastoreCursor
from .protocols import IDatastoreKey
from .protocols import IDatastoreEntity
from .protocols import IDatastoreTransaction


T = TypeVar('T', bound=pydantic.BaseModel)


class BaseDatastoreStorage:
    dump_mode: str = 'python'
    exclude_fields: set[str] = set()
    exclude_none: bool = False

    @class_property
    def __signature__(cls) -> inspect.Signature:
        return merge_signatures([
            inspect.signature(cls.__init__),
            inspect.signature(cls.require)
        ])

    @staticmethod
    async def run_in_executor(
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

    def __init__( # type: ignore
        self,
        *,
        client: Client,
        **kwargs: Any
    ) -> None:
        self.client = client
        self.require(**kwargs)

    def require(self, **_: Any):
        pass

    async def allocate_identifier(self, cls: type | str) -> int:
        if not isinstance(cls, str):
            cls = cls.__name__
        base = self.entity_key(kind=cls)
        result = await self.run_in_executor(
            functools.partial( # type: ignore
                self.client.allocate_ids, # type: ignore
                incomplete_key=base,
                num_ids=1
            )
        )
        return [x for x in result][0].id

    async def destroy(self, obj: Any) -> None:
        key = self.entity_key(type(obj), obj.pk)
        await self.run_in_executor(
            functools.partial(
                self.client.delete, # type: ignore
                key=key
            )
        )

    def dump_model(
        self,
        obj: pydantic.BaseModel,
        exclude_fields: set[str] | dict[str, Any] | None = None,
        exclude_none: bool = False
    ) -> dict[str, Any]:
        return obj.model_dump(
            mode=self.dump_mode,
            exclude=exclude_fields or self.exclude_fields,
            exclude_none=exclude_none or self.exclude_none
        )

    def entity_factory(
        self,
        key: IDatastoreKey,
        obj: pydantic.BaseModel,
        exclude_fields: set[str] | dict[str, Any] | None = None,
    ) -> IDatastoreEntity:
        entity = cast(IDatastoreEntity, self.client.entity(key)) # type: ignore
        attrs = self.dump_model(obj, exclude_fields=exclude_fields)
        if attrs:
            entity.update(attrs) # type: ignore

        # Run some validation to ensure that the entity can be
        # persisted in datastore. TODO: convert this to a
        # pydantic TypeAdapter.
        for k, v in dict(entity).items():
            if isinstance(v, set):
                entity[k] = list(cast(set[Any], v))
        return entity

    def entity_key(
        self,
        kind: str | type,
        identifier: int | str | None = None,
        parent: IDatastoreKey | None = None,
        namespace: str | None = None
    ) -> IDatastoreKey:
        if not isinstance(kind, str):
            kind = self.get_entity_name(kind)
        if isinstance(identifier, ResourceIdentifier):
            identifier = identifier.cast() # type: ignore
        args: list[Any] = [kind]
        if identifier is not None:
            args.append(identifier)
        return self.client.key(*args, parent=parent, namespace=namespace) # type: ignore

    def get_entity_name(self, cls: type[Any]) -> str:
        return cls.__name__

    def model_factory(self, entity: Mapping[str, Any], model: type[T]) -> T:
        obj = model.model_validate(dict(entity))
        if isinstance(obj, PersistedModel):
            obj.attach(self) # type: ignore
        return obj

    def query(
        self,
        model: type[T],
        filters: Iterable[tuple[str, str, Any]] | None = None,
        sort: Iterable[str] | None = None,
        namespace: str | None = None,
        limit: int | None = None,
        kind: str | None = None,
        page_size: int = 10,
        keys: list[IDatastoreKey] | None = None,
        **_: Any
    ) -> DatastoreCursor[T]:
        flattened: list[tuple[str, str, Any]] = []
        for attname, op, value in list(filters or []):
            if not isinstance(value, list):
                flattened.append((attname, op, value))
                continue
            flattened.extend([(attname, op, x) for x in value]) # type: ignore
        return DatastoreCursor(
            kind=kind or self.get_entity_name(model),
            model=model,
            client=self.client,
            keys=keys,
            filters=flattened,
            namespace=namespace,
            sort=sort,
            limit=limit,
            page_size=page_size
        )

    async def find(
        self,
        kind: type[T],
        filters: Iterable[tuple[str, str, int | str]],
        sort: Iterable[str] | None = None
    ) -> AsyncIterable[T]:
        q = self.client.query(kind=kind.__name__) # type: ignore
        if sort is not None:
            q.order = sort
        for filter in filters:
            q.add_filter(*filter) # type: ignore
        results = await self.run_in_executor(
            functools.partial(q.fetch) # type: ignore
        )
        for entity in results:
            yield kind.model_validate(dict(entity))

    async def get_entity_by_key(self, key: IDatastoreKey) -> IDatastoreEntity | None:
        return await self.run_in_executor(
            functools.partial(
                self.client.get, # type: ignore
                key=key
            )
        )

    async def get_model_by_key(
        self,
        cls: type[T],
        pk: int | str,
        parent: IDatastoreKey | None = None,
        namespace: str | None = None
    ) -> T | None:
        entity = await self.get_entity_by_key(
            key=self.entity_key(cls, pk, parent=parent, namespace=namespace)
        )
        if entity is None:
            return None
        return await self.restore(self.model_factory(dict(entity), cls))

    async def put(
        self,
        obj: pydantic.BaseModel,
        pk: int | str,
        parent: IDatastoreKey | None = None,
        exclude_fields: set[str] | dict[str, Any] | None = None,
        transaction: IDatastoreTransaction | None = None
    ) -> IDatastoreKey:
        put = self.client.put if transaction is None else transaction.put # type: ignore
        key = self.entity_key(type(obj), pk, parent=parent)
        entity = self.entity_factory(key, obj, exclude_fields=exclude_fields)
        await self.run_in_executor(put, entity) # type: ignore
        return entity.key # type: ignore

    async def restore(self, instance: T) -> T:
        return instance 

    @contextlib.asynccontextmanager
    async def transaction(self, transaction: ITransaction | None = None):
        tx = cast(IDatastoreTransaction, await self.run_in_executor(self.client.transaction)) # type: ignore
        await self.run_in_executor(tx.__enter__)
        try:
            yield tx
        except Exception as e:
            await self.run_in_executor(tx.__exit__, type(e), e, None)
            raise
        await self.run_in_executor(tx.__exit__, None, None, None)