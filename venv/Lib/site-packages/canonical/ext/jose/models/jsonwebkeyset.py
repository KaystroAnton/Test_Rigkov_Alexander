# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pydantic

from .jsonwebkey import JSONWebKey


class JSONWebKeySet(pydantic.BaseModel):
    keys: list[JSONWebKey] = []
    _index: dict[str, JSONWebKey] = {}

    def has(self, *, kid: str | None = None, thumbprint: str | None = None) -> bool:
        """Return a boolean indicating if the given `kid` or
        `thumbprint` is in the JSON Web Key Set (JWKS).
        """
        return any([
            kid is not None and f'kid:{kid}' in self._index,
            thumbprint is not None and f'thumbprint:{thumbprint}' in self._index,
        ])

    def get(self, *, kid: str | None = None, thumbprint: str | None = None) -> JSONWebKey:
        if not (bool(kid) ^ bool(thumbprint)):
            raise TypeError(
                "The 'kid' and 'thumbprint' parameters are "
                "mutually exclusive."
            )
        k = ''
        if kid:
            k = f'kid:{kid}'
        if thumbprint:
            k = f'thumbprint:{thumbprint}'
        return self._index[k]

    def model_post_init(self, _: Any) -> None:
        for key in self.keys:
            self._index[f'thumbprint:{key.thumbprint}'] = key
            if key.kid is not None:
                self._index[f'kid:{key.kid}'] = key

    def verify(
        self,
        signature: bytes,
        payload: bytes,
        *,
        kid: str | None = None,
        alg: str | None = None
    ) -> bool:
        if kid is None:
            raise NotImplementedError
        is_valid = False
        if self.has(kid=kid):
            jwk = self.get(kid=kid)
            is_valid = jwk.verify(signature, payload, alg=alg)
        return is_valid