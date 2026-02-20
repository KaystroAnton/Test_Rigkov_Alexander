# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal
from typing import TypeVar

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.padding import AsymmetricPadding
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import HashAlgorithm
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.hashes import SHA384
from cryptography.hazmat.primitives.hashes import SHA512

from canonical.ext.jose.types import KeyOpEnum
from .rsakey import RSAKey


A = TypeVar('A')
O = TypeVar('O')
U = TypeVar('U')


class RSAVerificationKey(
    RSAKey[
        Literal[
            'RS256',
            'RS384',
            'RS512',
            'PS256',
            'PS384',
            'PS512',
        ],
        Literal[KeyOpEnum.verify],
        Literal['sig']
    ]
):

    def get_digest_algorithm(self) -> type[HashAlgorithm]:
        match self.alg:
            case 'PS256': alg = SHA256
            case 'PS384': alg = SHA384
            case 'PS512': alg = SHA512
            case 'RS256': alg = SHA256
            case 'RS384': alg = SHA384
            case 'RS512': alg = SHA512
            case _: raise NotImplementedError
        return alg

    def get_padding_class(self) -> type[AsymmetricPadding]:
        match self.alg:
            case 'RS256': padding = PKCS1v15
            case 'RS384': padding = PKCS1v15
            case 'RS512': padding = PKCS1v15
            case _: raise NotImplementedError
        return padding

    def get_padding_params(
        self,
        padding_class: type[AsymmetricPadding],
        digest_class: type[HashAlgorithm],
    ) -> dict[str, Any]:
        if padding_class != PKCS1v15:
            raise NotImplementedError
        return {}

    def verify(
        self,
        signature: bytes,
        payload: bytes,
        *,
        alg: str | None = None
    ) -> bool:
        public = self._public_key
        hasher = self.get_digest_algorithm()()
        try:
            public.verify(
                signature,
                payload,
                padding=self.get_padding(),
                algorithm=hasher
            )
            return True
        except InvalidSignature:
            return False