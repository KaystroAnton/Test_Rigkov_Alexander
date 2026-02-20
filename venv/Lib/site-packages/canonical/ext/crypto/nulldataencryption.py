# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TypeVar

from .bases import BaseDEK


T = TypeVar('T')


class NullDataEncryption(BaseDEK):
    __module__: str = 'canonical.ext.crypto'

    async def decrypt(self, ct: T, decoder: type[T] = bytes) -> T:
        self.logger.critical(
            "Decryption is not implemented, returning %s.",
            type(ct).__name__
        )
        return ct

    async def encrypt(self, value: Any, encoder: type = bytes) -> Any:
        self.logger.critical(
            "Encryption is not implemented, returning %s.",
            type(value).__name__
        )
        return value