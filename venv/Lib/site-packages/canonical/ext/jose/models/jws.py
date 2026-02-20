# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
from typing import cast
from typing import Any
from typing import ClassVar
from typing import Callable

import pydantic

from canonical.lib.utils.encoding import b64decode_json
from canonical.ext.jose.protocols import ITokenSignatureVerifier
from canonical.ext.jose.types import JWSCompactEncoded
from canonical.ext.jose.types import JWTDict
from .jwt import JWT
from .signature import Signature


class JWS(pydantic.BaseModel):
    CompactEncoded: ClassVar[type[JWSCompactEncoded]] = JWSCompactEncoded
    signatures: list[Signature] = pydantic.Field(
        default=...
    )
    claims: dict[str, Any] = {}
    payload: bytes

    @classmethod
    def require(cls, func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def f(self: pydantic.RootModel[Any], *args: Any, **kwargs: Any):
            if isinstance(self.root, cls.CompactEncoded):
                self.root = self.root.jose(cls)
            if not isinstance(self.root, cls):
                raise TypeError(
                    f"{type(self).__name__} is not a JSON Web Signature."
                )
            return func(self, *args, **kwargs)
        return f

    def compact(self):
        return JWSCompactEncoded(bytes.decode(self.encode_compact(), 'ascii'))

    def encode(self, compact: bool = True) -> bytes:
        """Encodes the JWS/JWE."""
        if len(self.signatures) > 1: # pragma: no cover
            raise ValueError("Compact encoding can not be used with multiple signatures.")
        return self.encode_compact()

    def encode_compact(self) -> bytes:
        assert len(self.signatures) == 1
        return self.signatures[0].encode(self.payload)

    def is_jwt(self) -> bool:
        """Return a boolean indicating if any of the signature headers says
        that the payload is a JWT.
        """
        return any([str.lower(h.typ or '') == 'jwt' for h in self.signatures])

    def __str__(self):
        return bytes.decode(bytes(self), 'ascii')

    def __bytes__(self):
        return self.encode_compact()

    async def verify(self, verifier: ITokenSignatureVerifier) -> bool:
        """Return a boolean indicating if at least one signature
        validated using the given verifier.
        """
        claims: JWTDict = {}
        if self.is_jwt():
            # TODO: This might raise an exception if the client specified
            # the typ header as JWT but the payload isn't.
            jwt = JWT.model_validate(b64decode_json(self.payload))
            claims = cast(JWTDict, jwt.model_dump())
        if not self.signatures:
            return False
        for signature in self.signatures:
            is_valid = await signature.verify(
                verifier=verifier,
                claims=claims,
                payload=self.payload
            )
            if not is_valid:
                continue
            break
        else:
            is_valid = False
        return is_valid