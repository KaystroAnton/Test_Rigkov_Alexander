# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from canonical.ext.oauth.bases import AuthorizationServerEndpoint
from canonical.ext.oauth.params import AuthorizationResponse
from canonical.ext.oauth.protocols import IRegisteredClient
from canonical.ext.oauth.resources import AuthorizationState
from canonical.ext.oauth.types import StopSnooping
from .useragentroutehandler import UserAgentRouteHandler


class ClientRedirectionEndpoint(AuthorizationServerEndpoint):
    cache_ttl: int = 3600
    name = 'oauth2.callback'
    params: AuthorizationResponse
    path = '/callback'
    route_class = UserAgentRouteHandler
    response_model = None
    status_code = 302
    summary = 'Redirection Endpoint'

    async def get(self):
        if not self.state.is_forwarding():
            raise NotImplementedError
        assert self.params.code
        self.state.status.update(
            metadata=self.state.metadata,
            status='Granted',
            code=self.params.code
        )
        await self.resources.persist(AuthorizationState, new=self.state)
        return fastapi.responses.RedirectResponse(
            status_code=302,
            url=self.state.get_return_url(
                iss=f'{self.request.url.scheme}://{self.request.url.netloc}'
            )
        )

    async def get_client(self) -> IRegisteredClient | None:
        return None

    async def setup(self):
        if self.params.state is None:
            raise StopSnooping
        try:
            self.state = await self.resources.get(
                key=self.params.state,
                model=AuthorizationState,
                require=True
            )
        except self.resources.DoesNotExist as e:
            raise StopSnooping from e