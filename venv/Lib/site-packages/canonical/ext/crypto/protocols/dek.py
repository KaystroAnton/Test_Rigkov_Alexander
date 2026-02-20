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
from typing import TypeVar


T = TypeVar('T')
EncryptionResult = TypeVar('EncryptionResult')


class IDataEncryption(Generic[EncryptionResult]):

    async def decrypt(
        self,
        ct: EncryptionResult,
        decoder: type[T] = bytes
    ) -> T:
        ...

    async def encrypt(
        self,
        value: Any,
        encoder: type = bytes
    ) -> EncryptionResult:
        ...