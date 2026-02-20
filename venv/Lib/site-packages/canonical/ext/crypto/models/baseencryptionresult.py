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


class BaseEncryptionResult(pydantic.BaseModel):
    alg: str = pydantic.Field(
        default=...,
        title="Algorithm",
        description="The algorithm used to perform the encryption function."
    )

    kid: str | None = pydantic.Field(
        default=None,
        title="Key Identifier",
        description=(
            "Identifies the key used to perform the encryption function."
        )
    )

    ct: Base64 = pydantic.Field(
        default=...,
        title="Ciphertext",
        description=(
            "The Base64-encoded encryption result."
        )
    )

    def __bytes__(self) -> bytes:
        return self.ct