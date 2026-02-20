# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import importlib
import inspect
from types import ModuleType
from typing import get_args
from typing import get_origin
from typing import Any
from typing import Iterable
from typing import Union

import fastapi

from canonical.ext.api import APIResourceType
from canonical.ext.api import APIVersionedMeta
from canonical.ext.api import APIModelInspector
from canonical.ext.cache import NullCache
from canonical.ext.resource import APIDescriptor
from canonical.ext.resource import APIGroupVersionList
from canonical.ext.resource import APIResourceList
from canonical.ext.resource import Error
from canonical.ext.resource import Resource
from canonical.ext.resource import ResourceServerList
from canonical.ext.resource import RootResource
from canonical.ext.iam.protocols import IResourceAuthorizationContext
from canonical.lib.protocols import ICache
from canonical.utils.http import MediaTypeSelector

from .apiroute import APIRoute
from .params import NegotiateResponseMediaType
from .resourceclient import ResourceClient
from .resourcerouter import ResourceRouter
from .response import Response


MediaType = NegotiateResponseMediaType({'application/yaml', 'application/json', "text/html"})


class ResourceApplication(fastapi.FastAPI):
    inspector: APIModelInspector = APIModelInspector()
    resource_paths: set[str] = set()
    media_types: MediaTypeSelector = MediaTypeSelector({
        'text/html',
        'application/json',
        'application/yaml'
    })

    def __init__(
        self,
        discovers: list[str] | None = None,
        *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self.router.route_class = APIRoute
        self.discovers = set(discovers or [])
        self.groups: dict[str, APIGroupVersionList] = {}
        self.resources: dict[str, dict[str, APIResourceList]] = {}
        self.add_api_route(
            methods=['GET'],
            path=f'/',
            endpoint=self.root,
            summary=f"Service descriptor",
            response_description=f"APIDescriptor object.",
            response_model=APIDescriptor,
            include_in_schema=True,
            tags=['Discovery Endpoints']
        )
        if self.discovers:
            self.add_api_route(
                methods=['GET'],
                path=f'/discover',
                endpoint=self.resource_servers,
                summary=f"Resource servers",
                response_description=f"ResourceServerList object.",
                response_model=ResourceServerList,
                include_in_schema=True,
                tags=['Discovery Endpoints']
            )

        @self.exception_handler(404)
        def _(request: fastapi.Request, _: Any) -> Any:
            assert request.client is not None
            return Response(
                media_type=self.media_types.select(request.headers.get('Accept')),
                status_code=404,
                content=Error.factory({
                    'status_code': 404,
                    'detail': "The server cannot find the requested resource",
                    'request': {
                        'url': str(request.url),
                        'host': request.client.host
                    }
                })
            )

    def add(
        self,
        impl: type[Resource[Any] | RootResource[Any] | ResourceRouter[Any]] | ModuleType | str,
        verbs: Iterable[str] | None = None,
        authorization: type[IResourceAuthorizationContext] | None = None,
        cache: ICache = NullCache(),
        **kwargs: Any
    ) -> None:
        root = fastapi.APIRouter(**kwargs)
        self.openapi_tags = self.openapi_tags or []
        verbs = set(verbs or [])
        if isinstance(impl, str):
            impl = importlib.import_module(f'{impl}.routers')
        if inspect.isclass(impl) and issubclass(impl, ResourceRouter):
            router: ResourceRouter[Any] = impl(enabled_verbs=verbs)
            router.add_to_application(
                app=root,
                register=self.register_resource,
                tags=self.openapi_tags,
                authorization=authorization,
                cache=cache
            )
        elif isinstance(impl, ModuleType):
            for _, value in inspect.getmembers(impl):
                if isinstance(value, ResourceRouter):
                    value.add_to_application(
                        app=root,
                        register=self.register_resource,
                        tags=self.openapi_tags,
                        authorization=authorization,
                        cache=cache
                    )
                    continue
                if isinstance(value, fastapi.APIRouter):
                    self.include_router(router=value)
        else:
            raise NotImplementedError
        self.include_router(router=root)

    def create_discovery_endpoint(
        self,
        meta: APIVersionedMeta[Any],
        resources: APIResourceList,
    ) -> None:

        async def discover(media_type: str = MediaType) -> Response[Any]:
            return Response(
                status_code=200,
                media_type=media_type,
                content=self.resources[meta.api_group][meta.version]
            )

        self.add_api_route(
            methods=['GET'],
            path=f'/{resources.path(meta.api_group)}',
            endpoint=discover,
            summary=f"{meta.api_group or 'default'} {meta.version}",
            response_description=f"The list of supported resources.",
            response_model=APIResourceList,
            include_in_schema=True,
            tags=['Discovery Endpoints']
        )

    def create_group_discovery_endpoint(self, api_group: str) -> None:
        async def discover(media_type: str = MediaType) -> Response[Any]:
            return Response(
                status_code=200,
                media_type=media_type,
                content=self.groups[api_group]
            )

        self.add_api_route(
            methods=['GET'],
            path=f'/{api_group}',
            endpoint=discover,
            summary=f"{api_group or 'core'}",
            response_description=f"The list of supported versions.",
            response_model=APIGroupVersionList,
            include_in_schema=True,
            tags=['Discovery Endpoints']
        )

    def openapi(self) -> dict[str, Any]:
        res = super().openapi()
        for _, method_item in res.get("paths", {}).items():
            for method, param in method_item.items():
                responses = param.get("responses")
                # remove default 422 - the default 422 schema is HTTPValidationError
                if "422" in responses and responses["422"]["content"][
                    "application/json"
                ]["schema"]["$ref"].endswith("HTTPValidationError"):
                    del responses["422"]
                for status_code, response in responses.items():
                    status_code = str(status_code)
                    if method == 'head' or status_code.startswith('3'):
                        response.pop('content', None)
                        continue

        return res

    def register_resource(self, model: type[APIResourceType], verb: str, plural: str | None = None) -> None:
        meta = self.inspector.inspect(model)
        if meta.api_group not in self.resources:
            self.resources[meta.api_group] = {}
            self.groups[meta.api_group] = APIGroupVersionList(group=meta.api_group)
            self.create_group_discovery_endpoint(meta.api_group)
        if meta.version not in self.resources[meta.api_group]:
            resources = self.resources[meta.api_group][meta.version] = APIResourceList(
                groupVersion=meta.version
            )
            self.groups[meta.api_group].add(resources)
            self.create_discovery_endpoint(meta, resources)
        resource = self.resources[meta.api_group][meta.version].add(meta, plural=plural)
        resource.add(verb)
        for root in self.inspector.get_root_types(model):
            self.register_resource(root, verb, plural=meta.plural)
            

    async def resource_servers(
        self,
        request: fastapi.Request,
        media_type: str = MediaType
    ) -> Response[ResourceServerList]: # type: ignore
        discovers = [f'{request.url.scheme}://{request.url.netloc}', *self.discovers]
        futures: list[asyncio.Future[Any]] = []
        async with ResourceClient(headers={'Accept': 'application/json'}) as client:
            for server in discovers:
                futures.append(
                    asyncio.ensure_future(client.discover_server(server))
                )
            return Response(
                status_code=200,
                media_type=media_type,
                content=ResourceServerList(
                    servers=await asyncio.gather(*futures)
                )
            )

    async def root(
        self,
        request: fastapi.Request,
        media_type: str = MediaType
    ) -> Response[APIDescriptor]: # type: ignore
        return Response(
            status_code=200,
            media_type=media_type,
            content=APIDescriptor(
                host=request.url.netloc,
                groups=list(self.groups.values())
            )
        )