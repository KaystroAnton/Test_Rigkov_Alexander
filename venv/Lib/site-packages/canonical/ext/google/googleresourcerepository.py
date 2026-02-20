# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
import logging
from typing import cast
from typing import Any
from typing import Iterable
from typing import Mapping
from typing import Any
from typing import TypeVar

import pydantic
from google.cloud.datastore import Client

from canonical.protocols import ITransaction
from canonical.ext.api import APIVersionedMeta
from canonical.ext.api import APIVersioned
from canonical.ext.api import ClusterObjectReference
from canonical.ext.api import DefaultInspector
from canonical.ext.api import LocalObjectReference
from canonical.ext.api import ObjectReference
from canonical.ext.api import OwnerReference
from canonical.ext.api import UIDReference
from canonical.ext.api.bases import BaseReference
from canonical.ext.api.annotations import Reference
from canonical.ext.api.annotations import APIResourceType
from canonical.ext.api.protocols import IObjectIdentifier
from canonical.ext.resource import BaseResourceRepository
from .basedatastorestorage import BaseDatastoreStorage
from .protocols import IDatastoreKey
from .protocols import IDatastoreEntity


B = TypeVar('B')
T = TypeVar('T', bound=APIResourceType)
SupportedKeyTypes = ClusterObjectReference, LocalObjectReference, ObjectReference, OwnerReference, UIDReference
KeyType = ClusterObjectReference | LocalObjectReference | ObjectReference | OwnerReference | UIDReference


class GoogleDatastoreResourceRepository(BaseResourceRepository):
    backend: BaseDatastoreStorage
    inspector = DefaultInspector
    logger: logging.Logger = logging.getLogger('uvicorn')

    def __init__(
        self,
        backend: BaseDatastoreStorage,
        **kwargs: Any
    ) -> None:
        super().__init__(inspector=self.inspector, **kwargs)
        self.backend = backend

    def all(self, model: type[B], namespace: str | None = None) -> BaseResourceRepository.Cursor[B]:
        return self.query(model=model, namespace=namespace)

    def get_entity_name(self, key: KeyType | type[T] | APIVersionedMeta[Any]) -> str:
        if isinstance(key, UIDReference):
            name = f'{key.api_group}/{key.kind}'
        elif isinstance(key, BaseReference):
            key = self.inspector.inspect(cast(type[APIVersioned], key.get_model()))
        else:
            key = self.inspector.inspect(cast(type[APIVersioned], key))
        name = f'{key.api_group}/{key.kind}'
        if not key.api_group:
            name = key.kind
        return name

    def model_factory(
        self,
        key: IDatastoreKey,
        entity: Mapping[str, Any],
        model: type[T]
    ) -> T:
        return model.model_validate(dict(entity))

    def resource_key(
        self,
        key: IObjectIdentifier[T] | Reference,
        parent: IDatastoreKey |None = None,
        namespace: str | None = None
    ) -> IDatastoreKey:
        assert isinstance(key, SupportedKeyTypes)
        return self.backend.entity_key(
            self.get_entity_name(key),
            key.as_name(),
            parent=parent,
            namespace=namespace or key.get_namespace()
        )

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
    ) -> BaseResourceRepository.Cursor[B]:
        q = self.backend.query(
            model=cast(type[pydantic.BaseModel], model),
            filters=filters,
            sort=sort,
            namespace=namespace,
            limit=limit,
            kind=kind or self.get_entity_name(cast(type[APIResourceType], model)),
            page_size=page_size,
            keys=keys
        )
        return cast(BaseResourceRepository.Cursor[B], q)
        

    async def allocate(self, obj: type[APIResourceType]) -> int:
        k = self.get_entity_name(obj)
        i = await self.backend.allocate_identifier(k)
        self.logger.info("Allocated identifier (kind: %s, uid: %s)", k, i)
        return i

    async def exists(self, key: Reference | Iterable[tuple[str, str, Any]], model: type[T]) -> bool:
        assert isinstance(key, BaseReference), type(key)
        q = self.backend.query(
            model=model,
            namespace=key.get_namespace(),
            keys=[self.resource_key(key, namespace=key.get_namespace())],
            page_size=1
        )
        return await q.exists()

    async def get_entity_by_key(self, key: IDatastoreKey) -> IDatastoreEntity | None:
        return await self.backend.get_entity_by_key(key)

    async def reference(
        self,
        key: IObjectIdentifier[T] | Reference,
        model: type[T],
    ) -> T | None:
        k = self.resource_key(key, namespace=key.get_namespace())
        e = await self.get_entity_by_key(key=k)
        instance = None
        if e is not None:
            instance = await self.restore(self.model_factory(k, dict(e), model))
        return instance

    def transaction(self, transaction: Any | None = None):
        return self.backend.transaction(transaction)

    async def persist_entity(
        self,
        client: Client | ITransaction,
        entity: IDatastoreEntity
    ) -> IDatastoreEntity:
        return await self.backend.run_in_executor(functools.partial(client.put, entity)) # type: ignore

    async def put(
        self,
        key: IObjectIdentifier[T] | Reference,
        dao: pydantic.BaseModel,
        transaction: Any | None = None
    ) -> None:
        await self.persist_entity(
            client=transaction or self.backend.client,
            entity=self.backend.entity_factory(
                key=self.resource_key(key),
                obj=dao
            )
        )