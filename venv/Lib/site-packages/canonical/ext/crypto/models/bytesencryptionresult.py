# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .baseencryptionresult import BaseEncryptionResult


class BytesEncryptionResult(BaseEncryptionResult):
    """The result of an encryption operation using the AES algorithm."""

    @property
    def aad(self) -> bytes:
        return b''

    @property
    def iv(self) -> None:
        return None

    @property
    def tag(self) -> None:
        return None

    def __bytes__(self) -> bytes:
        return self.ct