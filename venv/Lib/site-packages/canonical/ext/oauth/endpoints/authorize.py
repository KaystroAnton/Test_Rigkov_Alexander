# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import fastapi

from canonical.ext.fastapi.params import ResourceRepository
from canonical.ext.oauth.bases import AuthorizationServerEndpoint
from canonical.ext.oauth.params import AuthorizationRequest
from canonical.ext.oauth.types import URLSafeClientID
from canonical.ext.oauth.protocols import IRegisteredClient
from canonical.ext.oauth.clusterclient import ClusterClient
from .useragentroutehandler import UserAgentRouteHandler


class AuthorizeEndpoint(AuthorizationServerEndpoint):
    cache_ttl: int = 3600
    client_resource: ClusterClient
    name = 'oauth2.authorize'
    params: AuthorizationRequest
    path = '/authorize'
    route_class = UserAgentRouteHandler
    response_model = None
    resources: ResourceRepository
    status_code = 302
    summary = 'Authorize Endpoint'

    @property
    def client(self) -> IRegisteredClient:
        assert self._client is not None
        return self._client

    def get_client_meta(self) -> tuple[URLSafeClientID, str, type]:
        assert isinstance(self.params.client_id, URLSafeClientID)
        return (
            self.params.client_id,
            self.params.client_id.cache_key,
            self.params.client_id.model
        )

    async def discover(self, client: Any):
        pass

    async def get(self) -> fastapi.Response:
        raise NotImplementedError

    async def setup(self):
        await super().setup()
        await self.discover(self.client)
        await self.validate_client(self.client, self.params)

    async def validate_client(self, client: IRegisteredClient, params: AuthorizationRequest):
        params.validate_client(client)