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

from .rsaverificationkey import RSAVerificationKey
from .symmetricencryptionkey import SymmetricEncryptionKey
from .symmetricsigningkey import SymmetricSigningKey


__all__: list[str] = [
    'JSONWebKey'
]


JWKType = Union[
    RSAVerificationKey,
    SymmetricEncryptionKey,
    SymmetricSigningKey
]


class JSONWebKey(pydantic.RootModel[JWKType]):

    @property
    def kid(self):
        return self.root.kid

    @property
    def thumbprint(self):
        return self.root.thumbprint

    def verify(
        self,
        signature: bytes,
        payload: bytes,
        *,
        alg: str | None = None
    ) -> bool:
        # Signature does not verify if the given algorithm does not
        # match the key algorithm.
        if len({alg, self.root.alg}) > 1:
            return False
        return self.root.verify(signature, payload, alg=alg)