# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from canonical.ext.oauth.bases import Endpoint
from canonical.ext.oauth.models.responses import TokenResponse
from canonical.ext.oauth.params import TokenEndpointClient
from canonical.ext.oauth.params import TokenRequest


class TokenEndpoint(Endpoint):
    name = 'oauth2.token'
    path = '/token'
    response_model = TokenResponse
    summary = 'Token Endpoint'

    async def post(
        self,
        client: TokenEndpointClient,
        params: TokenRequest
    ):
        print(client)
        print(params.model_dump_json(indent=2))