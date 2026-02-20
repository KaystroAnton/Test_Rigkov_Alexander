# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from canonical.ext.oauth.bases import AuthorizationServerEndpoint
from canonical.ext.oauth.models import ServerMetadata
from canonical.ext.oauth.protocols import IRegisteredClient


class MetadataEndpoint(AuthorizationServerEndpoint):
    name = 'oauth2.metadaya'
    path = '/.well-known/oauth-authorization-server'
    response_model = ServerMetadata
    summary = 'Metadata Endpoint'

    async def get(self) -> ServerMetadata:
        return ServerMetadata.model_validate({
            'issuer': f'{self.request.url.scheme}://{self.request.url.netloc}',
            'authorization_endpoint': str(self.request.url_for('oauth2.authorize')),
            'token_endpoint': str(self.request.url_for('oauth2.token')),
            'authorization_response_iss_parameter_supported': True
        })

    async def get_client(self) -> IRegisteredClient | None:
        return None