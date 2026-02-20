# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging
from typing import Any
from typing import TypeVar

import pydantic

from ..models import EncryptionResult
from ..protocols import IDataEncryption


T = TypeVar('T')


class BaseDEK(IDataEncryption[EncryptionResult]):
    __module__: str = 'canonical.ext.crypto.bases'
    logger: logging.Logger = logging.getLogger('uvicorn')

    async def decrypt(
        self,
        ct: EncryptionResult,
        decoder: type[T] = bytes
    ) -> T:
        self.logger.debug("Decrypting (encoder: %s)", repr(decoder))
        adapter: pydantic.TypeAdapter[T] = pydantic.TypeAdapter(decoder)
        pt = await self.perform_decrypt(ct)
        return adapter.validate_json(pt)

    async def encrypt(
        self,
        value: Any,
        encoder: type = bytes
    ) -> EncryptionResult:
        if isinstance(value, EncryptionResult):
            # Only here to suppress warnings (TODO).
            return value
        self.logger.debug("Encrypting (encoder: %s)", repr(encoder))
        adapter: pydantic.TypeAdapter[bytes] = pydantic.TypeAdapter(encoder)
        buf = value
        if not isinstance(value, bytes):
            buf = adapter.dump_json(value, warnings=False)
        assert isinstance(buf, bytes)
        return await self.perform_encrypt(buf)

    async def perform_decrypt(self, ct: EncryptionResult) -> bytes:
        raise NotImplementedError

    async def perform_encrypt(self, value: bytes) -> EncryptionResult:
        raise NotImplementedError