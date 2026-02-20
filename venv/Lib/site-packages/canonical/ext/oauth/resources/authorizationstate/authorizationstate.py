# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Union

import httpx
import pydantic

from canonical.ext.api import APIResourceModel
from canonical.ext.oauth.models.responses import AuthorizationResponse
from canonical.ext.oauth.models.responses import TokenResponse
from canonical.ext.oauth.models.requests import AuthorizationCodeRequest
from canonical.ext.oauth.protocols import IObtainingClient
from .authorizationstatestatus import AuthorizationRequestStateStatus
from .forwardingstatespec import ForwardingStateSpec
from .issuingstatespec import IssuingStateSpec
from .obtainingstatespec import ObtainingStateSpec
from .proxyingstatespec import ProxyingStateSpec


AuthorizationStateSpecType = Union[
    ForwardingStateSpec,
    IssuingStateSpec,
    ObtainingStateSpec,
    ProxyingStateSpec,
]


class AuthorizationState(
    APIResourceModel[str],
    group='oauth',
    version='v2',
    plural='authorizationstates'
):
    """Describes the state of an OAuth 2.x/OpenID Connect
    authorization request.
    """
    spec: AuthorizationStateSpecType = pydantic.Field(
        default=...,
        title="Specification",
        description=(
            "Specifies the parameters of the authorization request."
        )
    )

    status: AuthorizationRequestStateStatus = pydantic.Field(
        default=...,
        description=(
            "Describes the current state of the AuthorizationRequest."
        )
    )

    def get_user_agent_redirect_uri(self) -> str:
        return self.spec.get_user_agent_redirect_uri(self.metadata)

    def is_failed(self) -> bool:
        return self.status.current == 'Failed'

    def is_forwarding(self) -> bool:
        return self.spec.redirect_mode == 'forwarding'

    def is_obtained(self) -> bool:
        return self.status.current == 'Obtained'

    def is_obtainable(self) -> bool:
        return self.spec.redirect_mode in {'issuing', 'proxy'}

    def is_proxy(self) -> bool:
        return self.spec.redirect_mode == 'proxy'

    async def obtain(
        self,
        http: httpx.AsyncClient,
        client: IObtainingClient[TokenResponse],
        params: AuthorizationResponse
    ):
        assert params.code is not None
        client = client.configure(
            server=self.spec.issuer,
            token_endpoint=self.spec.token_endpoint
        )
        response = await client.obtain(
            grant=AuthorizationCodeRequest(
                grant_type='authorization_code',
                code=params.code,
                redirect_uri=self.spec.get_redirect_uri()
            ),
            http=http
        )
        if not response.is_error():
            assert isinstance(response, TokenResponse)
            self.status.update(self.metadata, **self.spec.on_obtained(response))
        else:
            self.status.update(
                metadata=self.metadata,
                status='Failed'
            )
        return response

    def get_return_url(self, iss: str) -> str:
        """Get the URL to redirect the user agent after succesfully
        obtaining an access code.
        """
        return self.spec.get_return_url(
            code=self.metadata.name,
            iss=iss
        )