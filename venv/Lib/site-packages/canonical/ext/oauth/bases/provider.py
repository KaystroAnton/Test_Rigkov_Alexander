# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Generic
from typing import TypeVar

import pydantic

from canonical.ext.api import APIResourceModel
from canonical.ext.httpx import AsyncClient
from .providerspec import BaseProviderSpec


T = TypeVar('T', bound=BaseProviderSpec)


class BaseProvider(APIResourceModel[str], Generic[T], abstract=True):
    spec: T = pydantic.Field(
        default=...,
        description=(
            "Specification of the OAuth 2.x/OpenID Connect provider."
        )
    )

    def is_discoverable(self):
        return self.spec.is_discoverable()

    async def discover(self, client: AsyncClient):
        return await self.spec.discover(client)