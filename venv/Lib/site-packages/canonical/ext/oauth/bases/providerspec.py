# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import httpx
import pydantic

from canonical.ext.api import ResourceSpec
from ..models import OIDCProvider
from ..models import ServerMetadata


class BaseProviderSpec(ResourceSpec):
    metadata: ServerMetadata | OIDCProvider = pydantic.Field(
        default=...,
        alias='serverMetadata',
        description=(
            "The metadata describing the authorization server."
        )
    )

    def is_discoverable(self):
        return isinstance(self.metadata, OIDCProvider)

    async def discover(self, client: httpx.AsyncClient):
        if not isinstance(self.metadata, ServerMetadata):
            self.metadata = await self.metadata.discover(client)
        return self.metadata