# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import contextlib
import copy
import secrets
from typing import Any
from typing import TypeVar

import httpx
import pydantic

from canonical.ext.cache import MemoryCache
from canonical.ext.httpx import AsyncClient
from canonical.ext.jose.protocols import ITokenSigner
from canonical.lib.protocols import ICache
from canonical.lib.types import HTTPResourceLocator
from canonical.lib.utils.http import MediaTypeSelector
from .models import OIDCProvider
from .models import ServerMetadata
from .models.requests import GrantModel
from .models.responses import TokenResponse
from .protocols import IObtainingClient
from .types import AuthenticationMethod
from .types import Error
from .types import ProtocolViolation
from .types import ResponseTypeLiteral


T = TypeVar('T', bound=pydantic.BaseModel)


class Client(IObtainingClient[TokenResponse]):
    __module__: str = 'canonical.ext.oauth'
    cache_ttl: int = 7200
    mode: AuthenticationMethod | None
    selector = MediaTypeSelector({"application/json"})

    @property
    def id(self) -> str:
        return self.client_id

    def __init__(
        self,
        server: str,
        client_id: str,
        *,
        client_secret: str | None = None,
        signer: ITokenSigner | None = None,
        mode: AuthenticationMethod | None = None,
        token_endpoint: str | None = None,
        authorization_endpoint: str | None = None,
        metadata_url: str | None = None,
        cache: ICache = MemoryCache(scope='global')
    ):
        self.cache = cache
        self.client_id = client_id
        self.client_secret = client_secret
        self.mode = mode
        self.signer = signer
        if mode is None and client_secret:
            self.mode = 'client_secret_post'
        if mode is None and signer:
            self.mode = 'private_key_jwt'
        if signer:
            self.signer = signer.configure(auto_now=True, auto_jti=True)
        adapter = pydantic.TypeAdapter(ServerMetadata | OIDCProvider)
        self.provider = adapter.validate_python({
            'issuer': server,
            'authorization_endpoint': authorization_endpoint,
            'token_endpoint': token_endpoint,
            'metadata_url': metadata_url,
            'protocol': 'oauth2:oidc'
        })

    def authorize(
        self,
        response_type: ResponseTypeLiteral
    ) -> HTTPResourceLocator:
        """Return a string containing the URL a user-agent must redirect
        to in order to authorize a grant.
        """
        assert isinstance(self.provider, ServerMetadata)
        if not self.provider.authorization_endpoint:
            raise NotImplementedError
        params: dict[str, str] = {
            'client_id': self.client_id,
            'state': secrets.token_hex()
        }
        if response_type:
            params['response_type'] = response_type
        return self.provider.authorization_endpoint.with_query(**params)

    def configure(self, **kwargs: Any) -> IObtainingClient[TokenResponse]:
        client = copy.deepcopy(self)
        client.provider = ServerMetadata.model_validate({
            **client.provider.model_dump(),
            **kwargs
        })
        return client

    async def create_client_assertion(
        self,
        provider: ServerMetadata,
        signer: ITokenSigner
    ) -> str:
        """Create a client assertion."""
        assert self.signer
        claims: dict[str, Any] = {
            'aud': provider.token_endpoint,
            'sub': self.client_id,
        }
        return await self.signer.sign_claims(claims, ttl=120)

    async def discover(self, http: httpx.AsyncClient | None) -> ServerMetadata:
        """Return a :class:`~canonical.ext.oauth.models.ServerMetadata`
        instance describing the authorization server and its capabilities.
        """
        assert self.provider
        if not isinstance(self.provider, ServerMetadata):
            provider = await self.cache.get(self.provider.issuer, ServerMetadata)
            if provider is None:
                async with self.http(http=http) as http:
                    provider = await self.provider.discover(http)
                assert isinstance(self.provider, OIDCProvider)
                await self.cache.set(
                    key=self.provider.issuer,
                    value=provider,
                    encoder=ServerMetadata,
                    ttl=self.cache_ttl
                )
            self.provider = provider
        return self.provider

    @contextlib.asynccontextmanager
    async def http(self, http: httpx.AsyncClient | None = None):
        if http is not None:
            yield http
            return
        async with AsyncClient() as http:
            yield http
            return

    async def obtain(
        self,
        grant: GrantModel[Any],
        http: httpx.AsyncClient | None = None
    ) -> TokenResponse | Error | ProtocolViolation:
        assert isinstance(self.provider, ServerMetadata)
        auth = None
        match self.mode:
            case 'client_secret_basic':
                assert self.client_secret
                auth = httpx.BasicAuth(self.client_id, self.client_secret)
            case 'client_secret_post':
                assert self.client_secret
                grant.identify(self.client_id)
                grant.set_client_secret(self.mode, self.client_secret)
            case 'private_key_jwt':
                assert self.signer is not None
                grant.assert_client(
                    type='urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
                    assertion=await self.create_client_assertion(self.provider, self.signer)
                )
            case 'client_secret_jwt':
                # TODO: Should do the same as private_key_jwt, but with a signer
                # that uses the client_secret.
                raise NotImplementedError(self.mode)
            case None:
                grant.identify(self.client_id)
            case _:
                raise NotImplementedError(self.mode)
        return await self._request(
            request=httpx.Request(
                method='POST',
                url=self.provider.token_endpoint,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                content=grant.model_dump_urlencoded()
            ),
            response_model=TokenResponse,
            auth=auth,
            http=http
        )

    async def _request(
        self,
        request: httpx.Request,
        response_model: type[T],
        http: httpx.AsyncClient | None = None,
        auth : httpx.Auth | None = None,
        accept: set[str] = {"application/json"}
    ) -> T | Error | ProtocolViolation:
        adapter: pydantic.TypeAdapter[response_model | Error | ProtocolViolation] =\
            pydantic.TypeAdapter(response_model | Error | ProtocolViolation)
        selector = MediaTypeSelector(accept)
        async with self.http(http) as http:
            response = await http.send(request, auth=auth)
            mt = selector.select(response.headers.get('Content-Type'))
            result = ProtocolViolation.model_validate(
                "The authorization server responded with an unexpected "
                f"content type: {response.headers.get('Content-Type')}."
            )
            if mt == "application/json":
                result = adapter.validate_json(response.content)
        return result

    def __repr__(self):
        return f'<Client: {self.client_id}@{self.provider.issuer}>'