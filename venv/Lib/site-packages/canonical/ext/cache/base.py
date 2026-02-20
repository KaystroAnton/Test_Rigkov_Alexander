# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import hashlib
import json
import logging
from typing import Any
from typing import Literal
from typing import TypeVar

import pydantic

from canonical.ext.crypto import EncryptionResult
from canonical.ext.crypto import IDataEncryption
from canonical.ext.crypto import NullDataEncryption
from canonical.lib.protocols import ICache


T = TypeVar('T')


class BaseCache(ICache):
    __module__: str = 'canonical.ext.cache'
    dek: IDataEncryption[EncryptionResult]
    logger: logging.Logger = logging.getLogger('uvicorn')

    def __init__(
        self,
        keyalg: Literal['sha256'] | None = None,
        prefix: str | None = None,
        dek: IDataEncryption[EncryptionResult] = NullDataEncryption()
    ):
        self.dek = dek
        self.keyalg = keyalg
        self.prefix = prefix

    def hash(self, value: str, algorithm: str | None = None) -> str:
        if self.prefix:
            value = f'{self.prefix}:{value}'
        algorithm = algorithm or self.keyalg
        if algorithm is not None:
            h = hashlib.new(algorithm)
            h.update(str.encode(value))
            value = h.hexdigest()
        return value

    async def serialize(
        self,
        value: T | EncryptionResult,
        encoder: type[T],
        encrypt: bool = False
    ) -> bytes:
        adapter = pydantic.TypeAdapter[T | EncryptionResult](encoder)
        if encrypt:
            value = await self.dek.encrypt(value, encoder)
        return adapter.dump_json(value)

    async def deserialize(self, value: bytes , decoder: type[T], mode: str) -> T:
        adapter = pydantic.TypeAdapter[T | EncryptionResult](decoder)
        match mode:
            case 'json':
                result = adapter.validate_python(json.loads(value))
            case 'python':
                result = adapter.validate_python(value)
            case _:
                raise NotImplementedError(mode)
        if isinstance(result, EncryptionResult):
            result = await self.dek.decrypt(result, decoder)
        return result

    async def get(
        self,
        key: str,
        decoder: type[T] = bytes,
        validation: Literal['strict', 'ignore'] = 'strict',
        mode: Literal['json'] = 'json',
        keyalg: Literal['sha256'] | None = None
    ) -> T | None:
        key = self.hash(key, algorithm=keyalg)
        value = await self.fetch(key)
        if value is None:
            self.logger.debug(
                self.logger.debug(
                    "Cache miss (key: %s, using: %s)",
                    key, type(self).__name__
                )
            )
            return None
        try:
            self.logger.debug("Cache hit (key: %s, using: %s)", key, type(self).__name__)
            assert isinstance(value, bytes)
            return await self.deserialize(value, decoder, mode)
        except (pydantic.ValidationError, ValueError, TypeError):
            if validation == 'strict':
                raise
            await self.clear(key)
            return None

    async def set(
        self,
        key: str,
        value: Any,
        encoder: type[T] = bytes,
        encrypt: bool = False,
        ttl: int | None = None,
        keyalg: Literal['sha256'] | None = None
    ) -> None:
        self.logger.debug("Cache write (key: %s, using: %s)", key, type(self).__name__)
        value = await self.serialize(value, encoder, encrypt=encrypt)
        await self.put(
            key=self.hash(key, algorithm=keyalg),
            value=value,
            encrypt=encrypt,
            ttl=ttl
        )

    async def clear(self, key: str) -> None:
        raise NotImplementedError

    async def fetch(self, key: str) -> bytes | None:
        raise NotImplementedError

    async def put(
        self,
        key: str,
        value: Any,
        encrypt: bool = False,
        ttl: int | None = None
    ) -> None:
        raise NotImplementedError