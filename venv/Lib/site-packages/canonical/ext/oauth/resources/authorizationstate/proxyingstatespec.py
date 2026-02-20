# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal

import pydantic

from canonical.ext.api import ObjectMeta
from canonical.ext.oauth.models.responses import TokenResponse
from canonical.ext.oauth.types import RedirectURI
from .authorizationstatespec import AuthorizationStateSpec


class ProxyingStateSpec(AuthorizationStateSpec[Literal['proxy']]):
    proxy_redirection_endpoint: RedirectURI = pydantic.Field(
        default=...,
        alias='proxyRedirectionEndpoint',
        title="Proxy Redirection Endpoint",
        description=(
            "The redirection endpoint of the intermediate OAuth 2.x/"
            "OpenID Connect proxy."
        )
    )

    def get_redirect_uri(self) -> RedirectURI | None:
        # For proxied requests, the redirect URI that the
        # authorization server has seen is the redirection
        # endpoint of the proxy, and we always include it.
        return self.proxy_redirection_endpoint

    def get_return_url(
        self,
        code: str,
        iss: str | None = None
    ) -> str:
        uri = self.params.redirect_uri or self.redirect_uri
        assert uri
        return uri.redirect(
            code=code,
            iss=iss,
            state=self.params.state
        )

    def get_user_agent_redirect_uri(
        self,
        metadata: ObjectMeta[str]
    ) -> str:
        return self.params.proxy(
            endpoint=self.authorization_endpoint,
            client_id=self.client_id,
            redirect_uri=str(self.get_redirect_uri()),
            state=metadata.name
        )

    def on_obtained(self, response: TokenResponse) -> dict[str, Any]:
        return {
            'status': 'Issued',
            'access_token': response.access_token,
            'refresh_token': response.refresh_token
        }