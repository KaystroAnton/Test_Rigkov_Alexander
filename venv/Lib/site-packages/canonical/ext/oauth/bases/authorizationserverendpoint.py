# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import cast

from canonical.ext.api import APIResourceType
from canonical.ext.fastapi.params import ResourceRepository
from canonical.ext.oauth.protocols import IRegisteredClient
from canonical.ext.oauth.types import URLSafeClientID
from .baseendpoint import BaseEndpoint


class AuthorizationServerEndpoint(BaseEndpoint):
    client_cache_ttl: int = 3600
    resources: ResourceRepository
    _client: IRegisteredClient | None

    def get_client_meta(self) -> tuple[URLSafeClientID, str, type]:
        raise NotImplementedError

    async def get_client(self) -> IRegisteredClient | None:
        client_id, cache_key, model = self.get_client_meta()
        client = cast(APIResourceType | None, await self.cache.get(cache_key, model))
        if client is None:
            client = await self.resources.get(client_id.ref)
            await self.cache.set(
                key=cache_key,
                value=client,
                encoder=model,
                ttl=self.client_cache_ttl
            )
        self.client_resource = client
        return cast(IRegisteredClient, getattr(client, 'spec'))


    async def setup(self):
        self._client = await self.get_client()
        setattr(self.request.state, 'oauth_client', self._client)