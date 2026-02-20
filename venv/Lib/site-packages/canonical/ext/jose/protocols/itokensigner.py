# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Protocol
from typing import Self


class ITokenSigner(Protocol):
    __module__: str = 'canonical.ext.jose'

    def configure(
        self,
        auto_now: bool = False,
        ttl: int | None = None,
        auto_jti: bool = False
    ) -> Self:
        ...

    async def sign_claims(self, claims: Any, ttl: int | None = None) -> str:
        ...