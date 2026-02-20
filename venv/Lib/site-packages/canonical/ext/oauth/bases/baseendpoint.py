# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import ClassVar

import fastapi
import fastapi.params
import pydantic

from canonical.ext.fastapi.params import HTTPClient
from canonical.lib.protocols import ICache
from .clientendpointroutehandler import ClientEndpointRouteHandler
from .endpointrequesthandler import EndpointRequestHandler


class BaseEndpoint:
    cache: ICache
    http: HTTPClient
    http_methods: ClassVar[list[str]] = [
        'GET',
        'HEAD',
        'POST',
        'PUT',
        'PATCH',
        'DELETE',
        'OPTIONS',
        'TRACE',
    ]

    dependencies: list[Any] = []
    model: Any
    name: str | None = None
    path: str
    request: fastapi.Request
    response_model: type[pydantic.BaseModel] | None
    route_class = ClientEndpointRouteHandler
    status_code: int = 200
    summary: str
    tags: list[str] = ['OAuth 2.x/OpenID Connect']

    @classmethod
    def as_endpoint(cls, method: str, **kwargs: Any) -> EndpointRequestHandler:
        return EndpointRequestHandler(
            endpoint=cls,
            handle=getattr(cls, method),
            **kwargs
        )

    @classmethod
    def as_router(
        cls,
        **kwargs: Any
    ) -> fastapi.APIRouter:
        router = fastapi.APIRouter(
            route_class=cls.route_class
        )
        for method in map(str.lower, cls.http_methods):
            if not hasattr(cls, method):
                continue
            router.add_api_route(
                methods=[str.upper(method)],
                path=cls.path,
                name=cls.name,
                endpoint=cls.as_endpoint(method, **kwargs),
                dependencies=cls.dependencies,
                status_code=cls.status_code,
                response_model=cls.response_model,
                response_model_by_alias=False,
                tags=list(cls.tags),
                **cls.get_openapi_params(method)
            )
        return router

    @classmethod
    def get_openapi_params(cls, method: str) -> dict[str, Any]:
        return {
            'summary': cls.summary
        }

    async def setup(self):
        pass

    async def _setup(self):
        await self.setup()