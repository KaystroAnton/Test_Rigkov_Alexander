# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import AsyncIterable
from typing import Generic
from typing import Protocol
from typing import TypeVar



T = TypeVar('T')


class IQuery(Protocol, Generic[T]):
    __module__: str = 'canonical.protocols'
    model: type[T]

    async def all(self) -> AsyncIterable[T]: ...
    async def one(self) -> T: ...
    async def first(self) -> T | None: ...
    async def exists(self) -> bool: ...