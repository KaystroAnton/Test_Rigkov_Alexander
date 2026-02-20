# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import hashlib
from typing import Any
from typing import Generic
from typing import Literal
from typing import TypeVar

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import AsymmetricPadding
from cryptography.hazmat.primitives.hashes import HashAlgorithm

from canonical.lib.types import Base64Int
from canonical.lib.utils.encoding import b64encode
from .base import BaseJWK


A = TypeVar('A')
O = TypeVar('O')
U = TypeVar('U')


class RSAKey(
    BaseJWK[
        Literal['RSA'], A, O, U
    ],
    Generic[A, O, U]
):
    e: Base64Int
    n: Base64Int
    _digest: type[HashAlgorithm]
    _public_numbers: rsa.RSAPublicNumbers
    _public_key: rsa.RSAPublicKey

    @property
    def thumbprint(self) -> str:
        message = self.model_dump_json(include={'e', 'kty', 'n'})
        return b64encode(hashlib.sha256(str.encode(message)).digest(), encoder=bytes.decode)

    def model_post_init(self, _: Any) -> None:
        self._public_numbers = rsa.RSAPublicNumbers(
            e=self.e,
            n=self.n
        )
        self._digest = self.get_digest_algorithm()
        self._public_key = self._public_numbers.public_key()

    def get_digest_algorithm(self) -> type[HashAlgorithm]:
        raise NotImplementedError

    def get_padding(self) -> AsymmetricPadding:
        cls = self.get_padding_class()
        return cls(**self.get_padding_params(cls, self._digest))

    def get_padding_class(self) -> type[AsymmetricPadding]:
        raise NotImplementedError

    def get_padding_params(
        self,
        padding_class: type[AsymmetricPadding],
        digest_class: type[HashAlgorithm],
    ) -> dict[str, Any]:
        raise NotImplementedError