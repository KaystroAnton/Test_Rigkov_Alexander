# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from canonical.ext.api import ClusterObjectReference
from canonical.ext.oauth.models import ServerMetadata
from canonical.ext.oauth.clusterprovider import ClusterProvider
from canonical.ext.oauth.clientspec import ClientSpec
from canonical.ext.oauth.resources import AuthorizationStateBuilder
from .authorize import AuthorizeEndpoint


class UpstreamAuthorizationEndpoint(AuthorizeEndpoint):
    #: Metadata describing the upstream authorzation server.
    metadata: ServerMetadata

    async def discover(self, client: ClientSpec[ClusterObjectReference]):
        provider = await self.resources.get(
            client.provider.with_model(ClusterProvider),
        )
        meta = await provider.discover(self.http)
        self.metadata = meta

    async def get(
        self,
        builder: AuthorizationStateBuilder = fastapi.Depends(AuthorizationStateBuilder)
    ) -> fastapi.Response:
        assert self.metadata.authorization_endpoint is not None
        assert self.metadata.token_endpoint is not None
        builder.with_authorization_endpoint(self.metadata.authorization_endpoint)
        builder.with_issuer(self.metadata.issuer)
        builder.with_token_endpoint(self.metadata.token_endpoint)
        builder.own(self.client_resource, controller=True)
        builder.proxy(str(self.request.url_for('oauth2.callback')))
        builder.with_client(self.client)
        builder.with_params(self.params)
        if not self.params.redirect_uri:
            builder.with_redirect_uri(self.client.default_redirect())
        state = await builder
        await self.resources.persist(type(state), state)
        return fastapi.responses.RedirectResponse(
            status_code=302,
            url=state.get_user_agent_redirect_uri(self.params)
        )