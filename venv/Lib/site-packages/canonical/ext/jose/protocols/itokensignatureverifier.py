# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Protocol

from canonical.ext.jose.types import JOSEHeaderDict
from canonical.ext.jose.types import JWTDict


class ITokenSignatureVerifier(Protocol):
    __module__: str = 'canonical.ext.jose'

    def is_selectable(self, header: JOSEHeaderDict, claims: JWTDict) -> bool:
        """Return a boolean indicating if the verifier is selectable,
        based on the claim in a JSON Web Token (JWT). The default
        implementation always returns ``True``.
        """
        return True

    async def verify_token(
        self,
        *,
        header: JOSEHeaderDict,
        claims: JWTDict,
        signature: bytes,
        payload: bytes,
    ) -> bool:
        ...
