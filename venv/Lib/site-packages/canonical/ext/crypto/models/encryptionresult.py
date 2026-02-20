# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Union

import pydantic

from .aesencryptionresult import AESEncryptionResult
from .bytesencryptionresult import BytesEncryptionResult
from .dhencryptionresult import DHEncryptionResult


EncryptionResultType = Union[
    AESEncryptionResult,
    BytesEncryptionResult,
    DHEncryptionResult
]
    

class EncryptionResult(pydantic.RootModel[EncryptionResultType]):

    @property
    def aad(self) -> bytes:
        return self.root.aad

    @property
    def iv(self) -> bytes | None:
        return self.root.iv

    @property
    def tag(self) -> bytes | None:
        return self.root.tag

    def __bytes__(self) -> bytes:
        return bytes(self.root)