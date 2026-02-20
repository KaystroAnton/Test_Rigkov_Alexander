# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Generic
from typing import Protocol
from typing import TypeVar

from canonical.exceptions import DoesNotExist
from canonical.exceptions import Duplicate
from .itransaction import ITransaction
from .ityped import ITyped


T = TypeVar('T')
M = TypeVar('M')
X = TypeVar('X', contravariant=True)


class IStorage(Protocol, Generic[T, X]):
    """The interface for storage classes. A storage class knows how
    to retrieve and persist objects of a specific type.
    """
    __module__: str = 'canonical.protocols'
    DoesNotExist: type[Exception] = DoesNotExist
    Duplicate: type[Exception] = Duplicate

    async def allocate(self, obj: Any | type[Any]) -> int:
        ...

    async def exists(self, key: Any) -> bool:
        ...

    async def delete(
        self,
        object: M,
        transaction: ITransaction | None = None,
        **kwargs: Any
    ) -> M: ...

    async def first(
        self,
        model: type[M],
        sort: list[str] | None = None,
        transaction: ITransaction | None = None,
        **kwargs: Any
    ) -> M | None:
        ...

    async def get(
        self,
        key: ITyped[M],
        *,
        model: type[M] | None = None,
        cached: bool = False,
        max_age: int = 0,
        transaction: ITransaction | None = None,
        **kwargs: Any
    ) -> M:
        ...

    async def persist(
        self,
        object: T,
        transaction: ITransaction | None = None,
        **kwargs: Any
    ) -> T:
        ...

    async def pop(
        self,
        key: ITyped[M] | int | str,
        model: type[M] | None = None,
        sort: list[str] | None = None,
        transaction: X | None = None,
        **kwargs: Any
    ) -> M:
        ...