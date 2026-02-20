# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
import inspect
import operator
from functools import reduce
from typing import Any
from typing import AsyncContextManager
from typing import AsyncIterable
from typing import cast
from typing import get_args
from typing import overload
from typing import Generator
from typing import Iterable
from typing import Literal
from typing import TypeVar
from typing import TYPE_CHECKING

import aiofiles
import pydantic
import yaml

from canonical.exceptions import DoesNotExist
from canonical.exceptions import Duplicate
from canonical.exceptions import Stale
from canonical.ext.crypto import NullDataEncryption
from canonical.ext.crypto.bases import BaseDEK
from canonical.ext.api.protocols import IObjectIdentifier
from ..annotations import APIResourceType
from ..annotations import Reference
from .resource import BaseResource
from .resourcedto import BaseResourceDTO
if TYPE_CHECKING:
    from ..apimodelinspector import APIModelInspector
    from ..objectmeta import ObjectMeta


B = TypeVar('B')
T = TypeVar('T', bound=APIResourceType)


class BaseResourceRepository:
    inspector: APIModelInspector
    DoesNotExist = DoesNotExist
    Duplicate = Duplicate
    Stale = Stale

    class Cursor(AsyncIterable[B]):
        def __await__(self) -> Generator[Any, Any, list[B]]:
            ...

    def __init__(
        self,
        inspector: APIModelInspector,
        dek: BaseDEK = NullDataEncryption()
    ):
        self.dek = dek
        self.inspector = inspector

    def all(self, model: type[B]) -> Cursor[B]:
        raise NotImplementedError

    def query(
        self,
        model: type[B],
        filters: Iterable[tuple[str, str, Any]] | None = None,
        sort: Iterable[str] | None = None,
        namespace: str | None = None,
        limit: int | None = None,
        kind: str | None = None,
        page_size: int = 10,
        keys: list[Any] | None = None,
        **_: Any
    ) -> Cursor[B]:
        raise NotImplementedError

    async def allocate(self, obj: type[Any]) -> int:
        raise NotImplementedError

    async def exists(
        self,
        key: Reference | Iterable[tuple[str, str, Any]],
        model: Any
    ) -> bool:
        raise NotImplementedError

    @overload
    async def get(
        self,
        key: IObjectIdentifier[T],
        *,
        require: Literal[True]
    ) -> T:
        ...

    @overload
    async def get(
        self,
        key: IObjectIdentifier[T],
        *,
        require: Literal[False]
    ) -> T:
        ...

    @overload
    async def get(
        self,
        key: IObjectIdentifier[T],
        model: None = None,
        *,
        require: Literal[True]
    ) -> T:
        ...

    @overload
    async def get(
        self,
        key: IObjectIdentifier[T],
        model: None = None,
        *,
        require: Literal[False] = False
    ) -> T:
        ...

    @overload
    async def get(
        self,
        key: str,
        model: type[T],
        *,
        require: Literal[True] = True
    ) -> T:
        ...

    @overload
    async def get(
        self,
        key: Reference,
        model: type[T],
        *,
        require: Literal[True]
    ) -> T:
        ...

    @overload
    async def get(
        self,
        key: Reference,
        model: type[T] | None,
        *,
        require: Literal[True] = True
    ) -> T:
        ...

    @overload
    async def get(
        self,
        key: Reference | str,
        model: type[T] | None,
        *,
        require: Literal[False] = False
    ) -> T | None:
        ...

    async def get(
        self,
        key: IObjectIdentifier[T] | Reference | str,
        model: type[T] | None = None,
        *,
        require: bool = True,
        namespace: str | None = None
    ) -> T | None:
        if not isinstance(key, str):
            if model is not None and key.get_model() != model:
                raise TypeError(
                    f"The model referenced by {type(key).__name__} must equal "
                    f"{model.__name__}."
                )
            model = cast(type[T] | None, key.get_model())
        if model is None:
            raise TypeError(
                f"Model should be attached to {type(key).__name__} "
                "or provided with the `model` parameter."
            )
        meta = self.inspector.inspect(model)
            
        # Do some checks if the key is a string. A string key specifies
        # the name of a non-deleted entity. For namespaced resources,
        # this makes the namespace parameter mandatory.
        if isinstance(key, str):
            # Handled in the reference() method.
            key = cast(IObjectIdentifier[T], meta.reference(name=key, namespace=namespace))

        # If the key does not have a model at this point, we assume
        # that it was provided through the model parameter.
        if not key.has_model():
            key.with_model(model)

        # Validate the namespace - must be None for cluster resources,
        # not none and not empty for namespaced resources.
        meta.validate_namespace(key.get_namespace())

        obj = await self.reference(key, model)
        if obj is None and require:
            raise self.DoesNotExist
        if obj is not None:
            await obj.decrypt(self.dek)
        return cast(T | None, obj)

    async def import_documents(
        self,
        kind: Any,
        path: str,
        iterator: bool = True
    ) -> AsyncIterable[APIResourceType]:
        loader: pydantic.TypeAdapter[BaseResourceDTO[APIResourceType]]
        models: list[type[pydantic.BaseModel]] = []
        for model in get_args(kind):
            if not inspect.isclass(model) or not issubclass(model, BaseResource):
                raise TypeError(
                    f"Member '{model.__name__}' of union `kind` is not "
                    "an implementation of BaseResource."
                )
            models.append(model.__create_model__)
        loader = pydantic.TypeAdapter(reduce(operator.or_, models))
        async with aiofiles.open(path) as f: # type: ignore
            documents = cast(list[dict[str, Any]], yaml.safe_load_all(await f.read())) # type: ignore
        for doc in documents:
            new = loader.validate_python(doc)
            old = await self.get(new.key, new.model, require=False)
            if old is not None:
                new = old.replace(new)
            else:
                new = new.factory(uid=await self.allocate(new.model))
            await self.persist(new.model, new, old=old)
            yield new

    async def persist(
        self,
        model: type[pydantic.BaseModel],
        new: T,
        *,
        transaction: Any = None,
        old: T | None = None
    ) -> T:
        async with self.transaction(transaction) as tx:
            assert new.metadata.is_attached()
            if old is None:
                try:
                    old = await self.get(new.key)
                except self.DoesNotExist:
                    old = None
            new = await self.persist_model(new, old=old, transaction=tx)
        return new

    async def persist_metadata(
        self,
        metadata: ObjectMeta[Any],
        transaction: Any | None = None
    ) -> None:
        dao = metadata.dao()
        await self.put(dao.key, dao, transaction=transaction)

    async def persist_model(
        self,
        new: T,
        old: T | None = None,
        transaction: Any = None
    ) -> T:
        if old and old.metadata.generation != new.metadata.generation:
            raise Stale
        updated, changed = new.update(old) # type: ignore
        if not changed:
            return new
        await updated.encrypt(self.dek)
        await self.put(updated.key, updated, transaction=transaction)
        await self.persist_metadata(updated.metadata, transaction=transaction)
        return updated

    async def put(
        self,
        key: IObjectIdentifier[T] | Reference,
        dao: pydantic.BaseModel,
        transaction: Any | None = None
    ) -> None:
        raise NotImplementedError(key)

    async def put_default(
        self,
        key: Reference,
        dao: pydantic.BaseModel,
        transaction: Any | None = None
    ) -> None:
        raise NotImplementedError(key)

    async def reference(
        self,
        key: IObjectIdentifier[T] | Reference,
        model: type[T],
    ) -> T | None:
        raise NotImplementedError

    async def restore(self, instance: T) -> T:
        return instance

    async def on_persisted(self, new: T, old: T | None, transaction: Any | None = None):
        pass

    def transaction(self, transaction: Any | None = None) -> AsyncContextManager[Any]:
        raise NotImplementedError