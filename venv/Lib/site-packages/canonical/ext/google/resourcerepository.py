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
from typing import AsyncIterable
from typing import TypeVar

import pydantic
from google.cloud.datastore import Client

from canonical.protocols import ITransaction
from canonical.protocols import ITyped
from canonical.ext.resource import IResourceRepository
from canonical.ext.resource import OwnerReference
from canonical.ext.resource import PrimaryKey
from canonical.ext.resource import ResourceStatus
from canonical.ext.resource import ResourceType
from canonical.ext.resource import ResourceTypeVar
from canonical.ext.resource import StatefulResource
from .basedatastorestorage import BaseDatastoreStorage
from .protocols import IDatastoreKey
from .protocols import IDatastoreEntity
from .protocols import IDatastoreTransaction


T = TypeVar('T')
M = TypeVar('M')


class ResourceRepository(BaseDatastoreStorage, IResourceRepository[IDatastoreTransaction]):
    cluster_namespace: str
    logger: logging.Logger = logging.getLogger('uvicorn')

    async def allocate(self, obj: type[ResourceType]) -> int:
        k = f'{obj.group}/{obj.__name__}'
        i = await self.allocate_identifier(k)
        self.logger.info("Allocated identifier (kind: %s, uid: %s)", k, i)
        return i

    def all(
        self,
        model: type[ResourceTypeVar],
        namespace: str | None = None
    ) -> AsyncIterable[ResourceTypeVar]:
        return self.query( # type: ignore
            model=model,
            namespace=namespace
        )

    def get_entity_name(self, cls: type[ResourceType]) -> str:
        name = f'{cls.group}/{cls.__name__}'
        if not cls.group:
            name = cls.__name__
        return name

    def resource_key(self, resource: ResourceType, model: type[ResourceType] | None = None) -> IDatastoreKey:
        args: list[Any] = [self.get_entity_name(model or type(resource)), resource.metadata.name]
        return self.client.key(*args, namespace=resource.get_namespace()) # type: ignore

    async def exists(self, key: ITyped[ResourceType] | OwnerReference) -> bool:
        if not isinstance(key, (OwnerReference, PrimaryKey)):
            raise NotImplementedError
        filters: list[tuple[str, str, Any]] = [
            ('metadata.name', '=', key.name)
        ]
        if isinstance(key, PrimaryKey):
            q = self.query(model=key.model, filters=filters, namespace=key.namespace)
        else:
            raise NotImplementedError
        return await q.exists()

    async def delete(
        self,
        object: M,
        transaction: ITransaction | None = None,
        **kwargs: Any
    ) -> M:
        raise NotImplementedError

    async def first(
        self,
        model: type[T],
        sort: list[str] | None = None,
        transaction: ITransaction | None = None,
        **kwargs: Any
    ) -> T | None:
        raise NotImplementedError

    async def get(
        self,
        key: ITyped[T],
        *,
        model: type[T] | None = None,
        cached: bool = False,
        max_age: int = 0,
        transaction: ITransaction | None = None,
        **kwargs: Any
    ) -> T:
        k = cast(PrimaryKey[pydantic.BaseModel], key) # type: ignore
        if cached:
            raise NotImplementedError
        obj = await self.get_model_by_key(
            cls=cast(type[pydantic.BaseModel], model) or k.get_type(),
            pk=k.name,
            namespace=k.get_namespace()
        )
        if obj is None:
            raise self.DoesNotExist
        return cast(T, obj)

    async def get_by_name(
        self,
        model: type[ResourceType],
        name: str | int,
        namespace: str | None = None
    ) -> ResourceType:
        obj = await self.get_model_by_key(model, name, namespace=namespace)
        if obj is None:
            raise self.DoesNotExist
        return obj

    async def persist(
        self,
        object: ResourceType,
        transaction: ITransaction | None = None,
        model: type[ResourceType] | None = None,
        **kwargs: Any
    ) -> ResourceType:
        async with self.transaction(transaction) as tx:
            exclude = {}
            if object.has_state():
                exclude = {
                    'status': {'conditions'}
                }
            key = self.resource_key(object, model=model)
            entity = self.entity_factory(
                key=key,
                obj=object,
                exclude_fields=exclude
            )
            await self.persist_entity(tx or self.client, entity)
            if object.has_state():
                await self.persist_status(cast(StatefulResource[Any, Any], object), key, tx)
        return object

    async def persist_entity(
        self,
        client: Client | ITransaction,
        entity: IDatastoreEntity
    ) -> IDatastoreEntity:
        return await self.run_in_executor(functools.partial(client.put, entity)) # type: ignore

    async def persist_status(
        self,
        object: StatefulResource[Any, ResourceStatus],
        key: IDatastoreKey,
        transaction: ITransaction
    ) -> None:
        if not object.status:
            return
        assert object.group
        for condition in object.status.conditions:
            if not condition.is_dirty():
                continue
            assert condition.uid is None
            dao = object.status.storage_model({
                **condition.model_dump(),
                'observed_generation': object.metadata.generation,
                'name': object.metadata.name,
                'namespace': object.metadata.get_namespace(),
                'parent': object.metadata.uid,
                'uid': await self.allocate_identifier('Condition')
            })

            # TODO: ensure that there are no other components writing
            # to the namespace.
            assert object.group
            entity = self.entity_factory(
                key=self.entity_key(
                    kind=f'{type(object).__name__}Condition',
                    identifier=dao.uid,
                    namespace=object.group
                ),
                obj=dao,
            )
            entity['parent'] = key
            await self.persist_entity(transaction, entity)

        # Also persist the status in the service namespace with
        # some additional metadata.
        status = object.clusterstate()

        assert isinstance(status.uid, str) or status.uid > 0
        entity = self.entity_factory(
            key=self.entity_key(
                kind=type(status).__name__,
                identifier=status.uid,
                namespace=object.group
            ),
            obj=status,
        )
        await self.persist_entity(transaction, entity)

    async def pop(
        self,
        key: ITyped[M] | int | str,
        model: type[M] | None = None,
        sort: list[str] | None = None,
        transaction: IDatastoreTransaction | None = None,
        **kwargs: Any
    ) -> M:
        raise NotImplementedError