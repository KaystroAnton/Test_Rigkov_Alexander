# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TypeVar

import fastapi

from canonical.ext.api import APIResourceType
from ..params import ResourceRepository
from ..params import RequestAuthorizationContext
from ..params import RequestObjectReference
from .default import Default


T = TypeVar('T', bound=APIResourceType)


class Exists(Default[T]):
    detail = True
    existing = False
    method = 'HEAD'
    status_code = 200
    verb = 'exists'

    async def authorize(self) -> None: # type: ignore
        pass

    async def exists(
        self,
        repo: ResourceRepository,
        key: RequestObjectReference
    ) -> bool:
        if key is None:
            return False
        self.logger.info(
            "Inspecting %s existence (key: %s)",
            self.model.__name__, key
        )
        return await repo.exists(key, self.model)

    async def handle( # type: ignore
        self,
        ctx: RequestAuthorizationContext,
        repo: ResourceRepository,
        key: RequestObjectReference,
    ) -> bool:
        if not ctx.is_authenticated() or not ctx.is_authorized():
            return False
        return await self.exists(repo, key)

    async def render_to_response(
        self,
        request: fastapi.Request,
        result: Any,
        media_type: str
    ) -> fastapi.Response: # type: ignore
        return fastapi.Response(
            media_type=media_type,
            status_code=200 if result else 404
        )

    def get_endpoint_summary(self) -> str:
        return f'Check if {self.model.__name__} exists'

    def get_openapi_responses(self) -> dict[int, dict[str, Any]]:
        return {
            **super().get_openapi_responses(),
            200: {
                'description': self.get_response_description()
            }
        }

    def get_response_description(self) -> str:
        return f'The {self.model.__name__} specified by the path parameter(s) exists.'