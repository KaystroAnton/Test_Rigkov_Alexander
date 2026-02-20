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

import pydantic

from canonical.ext.api import ObjectMeta
from canonical.ext.api import ResourceSpec
from canonical.lib.types import HTTPResourceLocator
from canonical.ext.oauth.models.requests import AuthorizationRequest
from canonical.ext.oauth.models.responses import TokenResponse
from canonical.ext.oauth.types import RedirectURI


M = TypeVar('M')


class AuthorizationStateSpec(ResourceSpec, Generic[M]):
    """Describes the state of an OAuth 2.x/OpenID Connect
    authorization request.
    """
    issuer: HTTPResourceLocator = pydantic.Field(
        default=...,
        title="Issuer",
        description=(
            "The issuer identifier of the authorization server."
        )
    )

    authorization_endpoint: HTTPResourceLocator = pydantic.Field(
        default=...,
        title="Authorization Endpoint",
        alias='authorizationEndpoint',
        description=(
            "The authorization endpoint to which the authorization "
            "request is issued, without query parameters."
        )
    )

    token_endpoint: HTTPResourceLocator = pydantic.Field(
        default=...,
        title="Token Endpoint",
        alias='tokenEndpoint',
        description=(
            "The token endpoint from which the token is obtained after "
            "receiving an authorization code."
        )
    )

    client_id: str = pydantic.Field(
        default=...,
        alias='clientId',
        title="Client ID",
        description=(
            "The client identifier of the **local** client. If "
            "`.clientId` equals `.params.client_id`, then this "
            "server is obtaining the access token. Otherwise, it "
            "is acting as a proxy or intermediate on the behalf "
            "of another server. In that case, the `.clientId` "
            "parameter points to the local client configuration "
            "that the server maintains."
        )
    )

    params: AuthorizationRequest = pydantic.Field(
        default=...,
        title="Parameters",
        description=(
            "The parameters of the authorization request, as specified "
            "by the OAuth 2.x/OpenID Connect specifications. Note that "
            "the fields in this object are not `pascalCase` to maintain "
            "conformance with the specifications."
        )
    )

    redirect_mode: M = pydantic.Field(
        default='proxy',
        alias='redirectMode',
        title="Redirect Mode",
        description=(
            "Specifies the redirection mode.\n\nIf `.mode` is `proxy`, then "
            "the obtained authorization code and other parameters are "
            "forwared unmodified to the clients' redirection endpoint (as "
            "specified by the `.redirectUri` parameter.\n\n"
            "With the `issue` mode, this server obtains the authorization "
            "code, and issues its own authorization code to pass back "
            "to the client.\n\nThe `obtain` mode indicates that the server "
            "itself wants to obtain the token (i.e. it is acting as a client "
            "application)."
        )
    )

    redirect_uri: RedirectURI | None = pydantic.Field(
        default=None,
        title="Redirect URI",
        alias='redirectUri',
        description=(
            "The redirection endpoint, if it differs from the `redirect_uri` "
            "query parameter in the authorization request.\n\n"
            "If the `redirect_uri` parameter was not included in the authorization "
            "request, this field holds the value that client selected."
        )
    )

    def get_user_agent_redirect_uri(
        self,
        metadata: ObjectMeta[str]
    ) -> str:
        raise NotImplementedError

    def get_redirect_uri(self) -> RedirectURI | None:
        """Return the redirect URI for use with the given
        audience.
        """
        uri = None
        if self.params.redirect_uri:
            uri = self.params.redirect_uri
        return uri

    def get_return_url(
        self,
        code: str,
        iss: str | None = None
    ) -> str:
        raise NotImplementedError
        

    def on_obtained(self, response: TokenResponse) -> dict[str, Any]:
        raise NotImplementedError