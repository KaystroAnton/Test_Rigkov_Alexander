# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import cast
from typing import Any

import pydantic

from canonical.lib.types import Base64
from canonical.lib.utils.encoding import b64encode
from canonical.lib.utils.encoding import b64decode_json
from canonical.ext.jose.protocols import ITokenSignatureVerifier
from canonical.ext.jose.types import JWTDict
from canonical.ext.jose.types import JOSEHeaderDict
from .jwsheader import JWSHeader


class Signature(pydantic.BaseModel):
    claims: JWSHeader
    protected: bytes | None = None
    header: dict[str, Any] = {}
    signature: Base64

    @pydantic.field_validator('protected', mode='before')
    def preprocess_protected(cls, value: bytes | str | None) -> bytes | None:
        if isinstance(value, str):
            value = str.encode(value, 'ascii')
        return value
    
    @pydantic.model_validator(mode='before') # type: ignore
    def preprocess(
        cls,
        values: dict[str, Any]
    ) -> dict[str, Any]:
        # The Header Parameter values used when creating or validating
        # individual signature or MAC values are the union of the two
        # sets of Header Parameter values that may be present: (1) the
        # JWS Protected Header represented in the "protected" member of
        # the signature/MAC's array element, and (2) the JWS Unprotected
        # Header in the "header" member of the signature/MAC's array element.
        # The union of these sets of Header Parameters comprises the JOSE
        # Header.  The Header Parameter names in the two locations MUST
        # be disjoint.
        claims = values.get('header') or {}
        protected = {}
        if values.get('protected'):
            protected = b64decode_json(values['protected'])
        if not isinstance(protected, dict):
            raise ValueError("The encoded protected header must be a JSON object.")
        if set(claims.keys()) & set(protected.keys()):
            raise ValueError(
                "The header parameter names in the protected and "
                "unprotected header must be disjoint."
            )
        values['claims'] = {**claims, **protected}
        return values

    @property
    def typ(self):
        return self.claims.typ

    def encode(self, payload: bytes) -> bytes:
        if self.protected is None: # pragma: no cover
            raise ValueError("Missing protected header.")
        return bytes.join(b'.', [
            self.protected,
            payload,
            b64encode(self.signature)
        ])

    async def verify(
        self,
        verifier: ITokenSignatureVerifier,
        claims: JWTDict,
        payload: bytes
    ) -> bool:
        assert self.protected is not None
        return await verifier.verify_token(
            header=cast(JOSEHeaderDict, self.claims.model_dump(by_alias=True)),
            claims=claims,
            signature=self.signature,
            payload=bytes.join(b'.', [self.protected, payload])
        )