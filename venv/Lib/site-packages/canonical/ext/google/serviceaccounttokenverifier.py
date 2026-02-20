# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging

from canonical.ext.cache import MemoryCache
from canonical.ext.httpx import AsyncClient
from canonical.ext.jose.models import JSONWebKeySet
from canonical.ext.jose.protocols import ITokenSignatureVerifier
from canonical.ext.jose.types import JOSEHeaderDict
from canonical.ext.jose.types import JWTDict
from canonical.lib.protocols import ICache


class ServiceAccountTokenVerifier(ITokenSignatureVerifier):
    cache_prefix: str = 'google:serviceaccount:jwks'
    cache_ttl: int = 3600
    jwks_endpoint: str = 'https://www.googleapis.com/service_accounts/v1/metadata/jwk'
    logger: logging.Logger = logging.getLogger('uvicorn')

    def __init__(
        self,
        http: AsyncClient,
        cache: ICache = MemoryCache(scope='global')
    ):
        self.cache = cache
        self.http = http

    def cache_key(self, email: str) -> str:
        return str.join(':', [self.cache_prefix, email])

    def is_selectable(self, header: JOSEHeaderDict, claims: JWTDict) -> bool:
        # When obtaining the token, the caller must set the `iss` claim to
        # the service account email. The `kid` header claim is assumed to
        # be always set by Google.
        return all([
            str.endswith(claims.get('iss') or '', '.iam.gserviceaccount.com'),
            'kid' in header,
            'alg' in header
        ])

    async def verify_token(
        self,
        *,
        header: JOSEHeaderDict,
        claims: JWTDict,
        signature: bytes,
        payload: bytes
    ) -> bool:
        if not self.is_selectable(header, claims):
            return False
        assert 'alg' in header
        assert 'kid' in header
        assert 'iss' in claims
        jwks = await self.get_service_account_jwks(claims['iss'])
        if not jwks.has(kid=header['kid']):
            return False
        return jwks.verify(signature, payload, kid=header['kid'], alg=header['alg'])

    async def get_service_account_jwks(self, email: str) -> JSONWebKeySet:
        jwks = await self.cache.get(self.cache_key(email), JSONWebKeySet)
        if jwks is None:
            response = await self.http.request(
                method='GET',
                url=f'{self.jwks_endpoint}/{email}',
                response_model=JSONWebKeySet,
                follow_redirects=True
            )
            jwks = JSONWebKeySet()
            if response.status_code >= 400:
                self.logger.warning(
                    "Unable to retrieve Google Service Account JWKS "
                    "(email: %s, status: %s url: %s)",
                    email, response.status_code, response.url
                )
            else:
                jwks = response.result
        return jwks