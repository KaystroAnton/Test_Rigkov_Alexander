# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal
from typing import TypeVar


T = TypeVar('T')


class ICache:
    __module__: str = 'canonical.lib.protocols'

    async def clear(self, key: str) -> None:
        ...

    async def get(
        self,
        key: str,
        decoder: type[T] = bytes,
        validation: Literal['strict', 'ignore'] = 'strict',
        mode: Literal['json'] = 'json',
        keyalg: Literal['sha256'] | None = None
    ) -> T | None:
        ...

    async def put(
        self,
        key: str,
        value: Any,
        encrypt: bool = False,
        ttl: int | None = None
    ) -> None:
        ...

    async def set(
        self,
        key: str,
        value: Any,
        encoder: type = bytes,
        encrypt: bool = False,
        ttl: int | None = None,
        keyalg: Literal['sha256'] | None = None
    ) -> None:
        """Set a key in the cache. Encode `value` using the given
        encoder if it is not a byte-sequence.
        """
        ...