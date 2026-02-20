# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Generic
from typing import TypeVar

import httpx
import pydantic

from canonical.ext.api import APIModelField
from canonical.ext.api import ResourceSpec
from canonical.ext.crypto import EncryptionResult
from canonical.ext.oauth.protocols import ITokenRequest
from .client import Client
from .models.responses import TokenResponse
from .types import AuthenticationMethod
from .types import Error
from .types import ProtocolViolation
from .types import RedirectURI
from .types import ResponseTypeLiteral


RefType = TypeVar('RefType')


class ClientSpec(ResourceSpec, Generic[RefType]):
    client_id: str = pydantic.Field(
        default=...,
        alias='clientId',
        title='Client ID',
        description=(
            "The OAuth 2.x/OpenID Connect client identifier."
        ),
        max_length=64
    )

    client_secret: EncryptionResult | str = APIModelField(
        default=...,
        alias='clientSecret',
        title='Client secret',
        description=(
            "The OAuth 2.x/OpenID Connect client secret."
        ),
        max_length=64,
        encrypt=True
    )

    provider: RefType = pydantic.Field(
        default=...,
        description=(
            "A local reference to an OAuth 2.x/OpenID Connect provider."
        )
    )

    response_type: ResponseTypeLiteral = pydantic.Field(
        default='code',
        title="Response type",
        alias='responseType',
        description=(
            "The default value for the `response_type` parameter in an "
            "authorization request."
        )
    )

    internal_redirect_uris: list[RedirectURI] = pydantic.Field(
        default_factory=list,
        title="Allowed redirection URIs",
        alias='internalRedirectUris',
        description=(
            "Specifies the set of URIs to which the server may "
            "redirect after an authorization request with the "
            "upstream authorization server."
        ),
    )

    authentication_method: AuthenticationMethod = pydantic.Field(
        default='client_secret_post',
        title="Default Authentication Method",
        description=(
            "Specifies the default authentication method that the client "
            "will use for all endpoints, unless the server is discoverable "
            "and its metadata tells the client to use a different method."
        )
    )

    @pydantic.field_validator('internal_redirect_uris', mode='after')
    def validate_redirect_uris(cls, value: list[RedirectURI]):
        if len(value) == 0:
            raise ValueError("At least one redirect uri must be specified.")
        return value

    @property
    def id(self) -> str:
        return self.client_id

    def allows_redirect(self, uri: str | None) -> bool:
        return uri is None or any([
            str(x) == uri for x
            in self.internal_redirect_uris
        ])

    def allows_response_type(self, response_type: str) -> bool:
        return self.response_type == response_type

    def configure(self, **kwargs: Any):
        kwargs.update({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'mode': self.authentication_method
        })
        return Client(**kwargs)

    def default_redirect(self) -> str:
        return str(self.internal_redirect_uris[0])

    def must_encrypt(self, attname: str) -> bool:
        return attname == 'client_secret'

    async def authenticate(self, request: ITokenRequest) -> None:
        if self.authentication_method != 'client_secret_post':
            raise NotImplementedError(self.authentication_method)
        assert not isinstance(self.client_secret, EncryptionResult)
        request.identify(self.client_id)
        request.set_client_secret(self.authentication_method, self.client_secret)

    async def obtain(
        self,
        grant: Any,
        http: httpx.AsyncClient | None = None
    ) -> TokenResponse | Error | ProtocolViolation:
        raise NotImplementedError