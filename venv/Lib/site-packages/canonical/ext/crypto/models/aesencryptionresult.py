# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from canonical.lib.types import Base64
from .baseencryptionresult import BaseEncryptionResult


class AESEncryptionResult(BaseEncryptionResult):
    """The result of an encryption operation using the AES algorithm."""
    aad: Base64 = pydantic.Field(
        default=b'',
        title="Additional Authenticated Data (AAD)",
        description=(
            "The Base64-encoded input data to the authenticated encryption "
            "function that is authenticated but not encrypted."
        )
    )

    ct: Base64 = pydantic.Field(
        default=...,
        title="Ciphertext",
        description=(
            "The Base64-encoded encryption result."
        )
    )

    iv: Base64 = pydantic.Field(
        default=...,
        title="Initialization Vector (IV)",
        description=(
            "A binary vector used as the input to initialize the algorithm for "
            "the encryption of a plaintext block sequence to increase security "
            "by introducing additional cryptographic variance and to synchronize "
            "cryptographic equipment. The initialization vector need not be secret."
        )
    )

    tag: Base64 = pydantic.Field(
        default=...,
        title="Authentication tag",
        description=(
            "A cryptographic checksum on data that is designed to reveal both "
            "accidental errors and the intentional modification of the data."
        )
    )