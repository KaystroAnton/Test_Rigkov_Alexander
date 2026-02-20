# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable
from typing import TypeVar


T = TypeVar('T')


class ICache(str):
    __module__: str = 'canonical.protocols'

    async def get(
        self,
        key: str,
        decoder: Callable[[bytes], T] = bytes
    ) -> T | None:
        ...

    async def set(
        self,
        key: str,
        value: Any,
        encoder: Callable[..., bytes] = bytes,
        encrypt: bool = False
    ) -> None:
        """Set a key in the cache. Encode `value` using the given
        encode if it is not a byte-sequence.
        """
        ...