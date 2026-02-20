# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import inspect
from typing import cast
from typing import overload
from typing import Any
from typing import AsyncContextManager
from typing import AsyncIterable
from typing import Generic
from typing import Iterable
from typing import Protocol
from typing import TypeVar

import aiofiles
import pydantic
import yaml


from canonical import TypedResourceName
from canonical.protocols import IStorage
from canonical.exceptions import DoesNotExist
from canonical.exceptions import MultipleObjectsReturned
from canonical.exceptions import Stale
from .iresourcequery import IResourceQuery
from .resource import Resource
from .rootresource import ResourceType
from .rootresource import RootResource


R = TypeVar('R', bound=Resource[Any] | RootResource[Any])
K = TypeVar('K')
T = TypeVar('T', bound=pydantic.BaseModel)
X = TypeVar('X', contravariant=True)


class IResourceRepository(IStorage[ResourceType, X], Protocol, Generic[X]):
    DoesNotExist = DoesNotExist
    MultipleObjectsReturned = MultipleObjectsReturned
    Stale = Stale

    def typed(self, model: type[R]) -> 'TypedResourceRepository[R]':
        return TypedResourceRepository(
            repo=self,
            model=model
        )

    def all(self, model: type[R], namespace: str | None = None) -> AsyncIterable[R]:
        ...

    async def allocate(self, obj: type[ResourceType]) -> int:
        ...

    async def get_by_name(self, model: type[R], name: str | int, namespace: str | None = None) -> R:
        ...

    async def import_documents(
        self,
        kind: Any,
        path: str,
        iterator: bool = True
    ) -> AsyncIterable[Resource[Any] | RootResource[Any]]:
        adapter = pydantic.TypeAdapter(kind)
        async with aiofiles.open(path) as f: # type: ignore
            documents: list[dict[str, Any]] = yaml.safe_load_all(await f.read()) # type: ignore
        async with self.transaction() as tx:
            for doc in documents:
                resource = cast(Resource[Any], adapter.validate_python(doc))
                await resource.persist(self, transaction=tx) # type: ignore
                yield resource

    def query(
        self,
        model: type[T],
        filters: Iterable[tuple[str, str, Any]] | None = None,
        sort: Iterable[str] | None = None,
        namespace: str | None = None,
        limit: int | None = None,
        kind: str | None = None,
        page_size: int = 10,
        keys: list[Any] | None = None,
        **kwargs: Any
    ) -> IResourceQuery[T]:
        ...


    def transaction(self, transaction: Any = None) -> AsyncContextManager[Any]:
        ...


class TypedResourceRepository(Generic[R]):
    model: type[R]

    def __init__(self, repo: IResourceRepository[X], model: type[R]):
        self.model = model
        self.repo = repo

    @overload
    async def get(self, d: TypedResourceName[R], namespace: str | None) -> R:
        ...

    @overload
    async def get(self, d: int | str, namespace: str | None) -> R:
        ...

    async def get(self, d: Any, *args: Any, **kwargs: Any) -> Any:
        if isinstance(d, TypedResourceName):
            return await self.repo.get_by_name(cast(TypedResourceName[R], d).model, d.id)
        elif inspect.isclass(d) and issubclass(d, (Resource, RootResource)):
            raise NotImplementedError
        elif isinstance(d, (int, str)):
            return await self.repo.get_by_name(self.model, d)
        else:
            raise NotImplementedError(f"Unsupported object type: {type(d).__name__}")