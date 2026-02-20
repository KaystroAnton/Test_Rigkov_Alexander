# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal

import httpx
import pydantic

from canonical.lib.types import HTTPResourceLocator
from .servermetadata import ServerMetadata


class OIDCProvider(pydantic.BaseModel):
    model_config = {'populate_by_name': True}

    protocol: Literal['oauth2:oidc']

    issuer: HTTPResourceLocator = pydantic.Field(
        default=...,
        description=(
            "The OpenID Connect Issuer Identifier."
        )
    )

    metadata_url: str | None = pydantic.Field(
        default=None,
        alias='metadataUrl',
        description=(
            "The metadata URL used for discovery, if the provider "
            "uses a non-standard path."
        )
    )

    async def discover(self, http: httpx.AsyncClient):
        metadata = None
        urls: list[str] = [
            f'{self.issuer}/.well-known/oauth-authorization-server',
            f'{self.issuer}/.well-known/openid-configuration'
        ]
        if self.metadata_url:
            urls = [self.metadata_url]
        for url in urls:
            response = await http.get(url)
            if response.status_code == 404:
                continue
            response.raise_for_status()
            metadata = ServerMetadata.model_validate(response.json())
            await metadata.discover(http=http)
            break
        if metadata is None:
            raise NotImplementedError
        return metadata