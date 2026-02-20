# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import copy
import inspect
import logging
from collections import OrderedDict
from typing import cast
from typing import get_args
from typing import get_origin
from typing import Any
from typing import Annotated
from typing import Callable
from typing import Generic
from typing import NoReturn
from typing import TypeVar

import fastapi
import fastapi.params
import pydantic
from fastapi.exceptions import HTTPException

from canonical.exceptions import Duplicate
from canonical.exceptions import Immutable
from canonical.exceptions import ReferentDoesNotExist
from canonical.exceptions import ProgrammingError
from canonical.ext.api import APIModelInspector
from canonical.ext.api import APIResourceType
from canonical.ext.api.bases import BaseResource
from canonical.ext.api.protocols import IResource
from canonical.ext.cache import NullCache
from canonical.ext.resource import Error
from canonical.ext.resource import ResourceType
from canonical.ext.resource import IResourceRepository
from canonical.ext.iam.protocols import IResourceAuthorizationContext
from canonical.lib.protocols import ICache
from canonical.utils import throw
from .headers import RESPONSE_CONTENT_TYPE
from .headers import RESPONSE_ETAG_RESOURCE
from ..params import AcceptedContentType
from ..params import NegotiateResponseMediaType
from ..params import RequestAuthorizationContext
from ..params import RequestObjectReference
from ..params import RequestResource
from ..params import RequestVerb
from ..params import ResourceRepository
from ..response import Response
from ..utils import inject
from .basemetaclass import BaseMetaclass
from .endpoint import Endpoint
from .validator import Validator


T = TypeVar('T')


class BaseOperation(Generic[T], metaclass=BaseMetaclass):
    authenticated: bool = True
    authorized: bool = True
    cache: ICache = NullCache()
    creates: bool = False
    dependants: list[Callable[..., Any]]
    dependencies: list[Any]
    description: str | None = None
    handle: Any
    include_in_schema: bool = True
    input_model: type[pydantic.BaseModel] | None = None
    input_params: set[str]
    inspector: APIModelInspector = APIModelInspector()
    logger: logging.Logger = logging.getLogger('uvicorn')
    method: str | None = None
    model: type[APIResourceType]
    path: str | None = None
    permissions: set[str]
    summary: str | None = None
    verb: str = ''

    default_responses: dict[int, Any] = {
        401: {
            'model': Error,
            'description': (
                "Authentication is required to perform the requested "
                "operation or the provided credential is invalid."
            ),
        },
        403: {
            'model': Error,
            'description': (
                "Untrusted credential or the authenticated request is not allowed "
                "to perform the requested operation."
            )
        },
        406: {
            'model': Error,
            'description': (
                "The media type accepted by the client can not be "
                "satisfied by the server."
            )
        },
        500: {
            'model': Error,
            'description': (
                "The server encountered an unexpected condition that "
                "prevented it from fulfilling the request."
            )
        }
    }
    detail: bool = False
    existing: bool = False
    requires_body: bool = False
    status_code: int = 200

    def __init__(
        self,
        *,
        model: type[APIResourceType],
        verb: str | None = None,
        method: str | None = None,
        path: str | None = None,
        permissions: set[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
        validator: type[Validator[Any]] = Validator,
        context_class: type[IResourceAuthorizationContext] | None = None,
        response_model: type[pydantic.BaseModel] | None = None,
        authenticated: bool = True,
        detail: bool | None = None,
        status_code: int | None = None,
        ttl: int | None = None,
        authorize: bool = True
    ) -> None:
        self.authorized = authorize
        self.authenticated = authenticated
        self.context_class = context_class
        self.description = description
        if detail is not None:
            self.detail = detail
        if self.detail and not self.creates:
            self.existing = True
        self.input_params = set()
        self.meta = self.inspector.inspect(model)
        self.method = method or self.method
        self.model = model
        self.path = self.path or path
        self.response_model = response_model
        self.status_code = status_code or self.status_code
        self.summary = summary
        self.ttl = ttl
        self.validator_class = validator
        self.views = self.inspector.get_models(model)
        if verb is not None:
            self.verb = verb
        if not self.verb:
            raise TypeError(
                f"{type(self).__name__}.__init__() missing 1 required "
                "positional argument: 'verb'"
            )
        self.dependants = []
        self.dependencies = [
            fastapi.Depends(self.context_class or (lambda: None)),
            fastapi.Depends(self.inject_verb(self.verb)),
            fastapi.Depends(self.inject_model),
        ]
        if not (300 <= self.status_code < 400):
            self.dependencies.extend([
                NegotiateResponseMediaType({
                    'text/html',
                    'application/yaml',
                    'application/json'
                }),
            ])
        self.permissions = set(permissions or [])
        if self.is_namespaced():
            self.dependencies.append(fastapi.Depends(self.inject_namespace))
        if self.is_detail():
            self.dependencies.append(fastapi.Depends(self.inject_name))
        if self.needs_existing():
            self.dependencies.append(fastapi.Depends(self.inject_existing))
        if self.input_model is not None:
            self.requires_body = True
        if self.requires_body:
            self.dependencies.extend([
                AcceptedContentType({'application/yaml', 'application/json'}),
                fastapi.Depends(self.inject_validator())
            ])
        if self.ttl is not None:
            self.dependencies.append(fastapi.Depends(self.inject_cache))

    def add_to_router(
        self,
        router: fastapi.FastAPI | fastapi.APIRouter,
        register: Callable[[type[APIResourceType], str], None],
        authorization: type[IResourceAuthorizationContext] | None = None,
        cache: ICache = NullCache(),
    ):
        self.cache = cache
        if authorization:
            self.dependencies = [
                *inject(resource_context=authorization),
                *self.dependencies
            ]
        router.add_api_route(
            methods=self.get_request_methods(),
            path=self.get_path(),
            endpoint=self.as_handler(),
            name=self.get_endpoint_name(),
            summary=self.get_endpoint_summary(),
            description=getattr(self.handle, '__doc__', None),
            dependencies=[*self.dependencies, fastapi.Depends(self.authorize)],
            include_in_schema=self.include_in_schema,
            responses={**self._get_openapi_responses()},
            response_description=self.get_response_description(),
            response_model=self.get_response_model(),
            response_model_by_alias=True,
            status_code=self.status_code,
            tags=[self.model.__name__],
            operation_id=self.get_endpoint_name()
        )
        register(self.model, self.verb)

    def annotate_handler(
        self,
        signature: inspect.Signature
    ) -> inspect.Signature:
        return signature

    def as_handler(self):
        # Do some modifications on the signatures because for
        # the base implementation classes, not every type is
        # known yet (i.e. the actual model).
        try:
            sig = inspect.signature(self.handle)
        except ValueError:
            raise TypeError(
                "Invalid signature for handler function or method. "
                f"Does {self.handle.__module__}.{self.handle.__name__}() "
                "take a verb.Verb instance as its first positional "
                "argument?"
            )
        params: OrderedDict[str, inspect.Parameter] = OrderedDict(sig.parameters)
        for param in sig.parameters.values():
            if not self.is_injectable(param):
                raise ProgrammingError(
                    f"Parameter '{param.name}' in handler "
                    f"{self.handle.__name__} is not injectable."
                )
            if param.annotation in (ResourceType, IResource, APIResourceType):
                params[param.name] = param.replace(annotation=self.get_model())
                continue
            if self.is_model(param.annotation) and not self.requires_body:
                # In this case, the annotation is assumed to point to the
                # existing resource.
                assert self.needs_existing()
                params[param.name] = param.replace(annotation=RequestResource)
                continue

            params[param.name] = param

        if not params.get('request'):
            params['request'] = inspect.Parameter(
                kind=inspect.Parameter.POSITIONAL_ONLY,
                name='request',
                annotation=fastapi.Request
            )

        sig = sig.replace(
            parameters=list(sorted(params.values(), key=lambda x: x.kind))
        )
        return Endpoint(
            name=self.get_endpoint_name(),
            signature=self.annotate_handler(sig),
            handle=self,
        )

    def depends(self, func: Callable[..., Any]) -> Callable[..., Any]:
        self.dependants.append(func)
        return func

    def fail(self, status_code: int, detail: str) -> NoReturn:
        raise HTTPException(status_code=status_code, detail=detail)

    def get_endpoint_name(self) -> str:
        return f'{self.meta.plural}.{self.verb}'

    def get_endpoint_summary(self) -> str:
        return self.summary or throw(NotImplementedError)

    def get_input_model(self) -> type[pydantic.BaseModel]:
        assert self.views.create is not None
        return self.views.create

    def get_model(self) -> type[pydantic.BaseModel]:
        return self.model

    def get_openapi_responses(self) -> dict[int, dict[str, Any]]:
        responses = copy.deepcopy(self.default_responses)
        if self.detail:
            responses[404] = {
                'model': Error,
                'description': (
                    f'The {self.model.__name__} specified by the path parameter(s) '
                    'does not exist.'
                )
            }
        if self.requires_body:
            responses[415] = {
                'model': Error,
                'description': "Invalid content type for request body."
            }
            responses[422] = {
                'model': Error,
                'description': "Invalid schema for request body."
            }
        if self.method == 'HEAD':
            responses.pop(406)

        if self.is_detail() and self.method in {'PUT', 'PATCH', 'DELETE'}:
            responses[412] = {
                'model': Error,
                'description': (
                    "The `If-Match` header mismatches with "
                    f"the existing {self.model.__name__}."
                )
            }

        return responses

    def get_path(self) -> str:
        path = f'{self.meta.base_path}'
        if self.detail:
            path = f'{path}/{{name}}'
        path = f'/{path}'
        if self.path:
            path = f'{path}{self.path}'
        return path

    def get_request_methods(self) -> list[str]:
        if self.method is None:
            raise ProgrammingError(
                f"{type(self).__name__}.method is None. Specify the attribute "
                f"or override {type(self).__name__}.get_request_methods()."
            )
        return [self.method] 

    def get_response_description(self) -> str:
        return self.description or throw(NotImplementedError)

    def get_response_model(self) -> type[pydantic.BaseModel] | None:
        if self.method == 'HEAD' or not (300 <= self.status_code < 400):
            return None
        if self.response_model:
            return self.response_model
        return self.model if (self.detail or self.creates) else self.model.List # type: ignore

    def has_response_model(self) -> bool:
        return (self.detail or self.creates)

    def inject_cache(
        self,
        cache_control: str | None = fastapi.Header(
            default=None,
            alias="Cache-Control",
            description=(
                "The `Cache-Control` header indicates the client preferences "
                "with regards to caching. Providing the `no-cache` directive "
                "requests the API server to serve to content directly from "
                "the primary data storage."
            )
        )
    ):
        pass

    def inject_name(
        self,
        request: fastapi.Request,
        name: str = fastapi.Path(
            description=f'The `.metadata.name` of an existing resource.',
            max_length=64,
        )
    ):
        setattr(request.state, 'name', name)

    def inject_namespace(
        self,
        request: fastapi.Request,
        namespace: str = fastapi.Path(
            description=(
                "Identifies the namespace that contains the "
                "resource."
            )
        ),
    ):
        setattr(request.state, 'namespace', namespace)

    def inject_model(self, request: fastapi.Request):
        setattr(request.state, 'model', self.model)

    def inject_validator(self):
        def f(request: fastapi.Request, validator: Validator[Any] = fastapi.Depends(self.validator_class)):
            setattr(request.state, 'validator', validator)
        return f

    def inject_verb(self, verb: str):
        def f(request: fastapi.Request):
            setattr(request.state, 'verb', verb)
        return f

    def is_annotated_dependency(self, value: Any) -> bool:
        if get_origin(value) != Annotated:
            return False
        args = get_args(value)
        if len(args) != 2:
            return False
        return isinstance(args[1], fastapi.params.Depends)

    def is_detail(self) -> bool:
        return self.detail

    def is_model(self, obj: Any) -> bool:
        return obj == self.model

    def is_injectable(self, p: inspect.Parameter):
        return any([
            p.annotation == fastapi.Request,
            p.annotation == IResource,
            p.annotation == APIResourceType,
            p.annotation == ResourceType,
            isinstance(p.default, fastapi.params.Path),
            isinstance(p.default, fastapi.params.Depends),
            self.is_annotated_dependency(p.annotation),
            inspect.isclass(p.annotation) and issubclass(p.annotation, pydantic.BaseModel),
            inspect.isclass(p.annotation) and issubclass(p.annotation, fastapi.Request)
        ])

    def is_namespaced(self) -> bool:
        return self.inspector.is_namespaced(self.model)

    def must_authenticate(self) -> bool:
        return self.authenticated

    def must_authorize(self) -> bool:
        return self.authorized

    def needs_existing(self) -> bool:
        return self.existing

    def on_not_authenticated(self):
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    def on_unauthorized(self):
        raise HTTPException(
            status_code=403,
            detail=(
                "The request subject is not granted permission "
                "to perform this operation."
            )
        )

    def replaces(self) -> bool:
        return False

    def resource(self, request: fastapi.Request) -> T:
        return getattr(request.state, 'resource')

    async def authorize(
        self,
        ctx: RequestAuthorizationContext,
        verb: RequestVerb
    ) -> None:
        # TODO : The permissions endpoint must be converted to a verb.
        if verb == 'authorize' or not self.must_authorize():
            return
        if not ctx.is_authenticated() and self.must_authenticate():
            self.on_not_authenticated()
        if not ctx.is_authorized():
            self.on_unauthorized()

        if self.permissions and not await ctx.has(self.permissions):
            raise NotImplementedError

    async def inject_existing(
        self,
        request: fastapi.Request,
        resources: ResourceRepository,
        key: RequestObjectReference,
        ifmatch: str | None = fastapi.Header(
            default=None,
            alias='If-Match',
            description=(
                "The `If-Match` header makes a request conditional. If present, "
                "It **must** match the current `.metadata.resourceVersion` value of "
                "the resource. If the values don't match then a `412 Precondition "
                "Failed` response is returned."
            )
        )
    ) -> None:
        if key is None:
            return None
        if ifmatch:
            raise NotImplementedError
        obj = None
        try:
            obj = await self.cache.get(
                key=key.cache_key(self.meta.cache_prefix),
                decoder=self.model
            )
            # Indicate that we retrieved the object from cache
            # so that we know not to cache it when responding.
            if obj is not None:
                setattr(request.state, 'cache_lookup', True)
        except pydantic.ValidationError:
            self.logger.warning(
                "Cache contained an object that violated the current "
                "schema (%s).",
                key
            )
        if obj is not None:
            setattr(request.state, 'resource', obj)
            return
        self.logger.debug("Retrieving resource (%s).", key)
        try:
            obj = await resources.get(key, cast(Any, self.model))
            assert obj is not None
        except resources.DoesNotExist:
            # TODO: Belongs on validator class.
            if self.needs_existing():
                self.fail(404, f'{self.model.__name__} does not exist.')
            obj = None
        setattr(request.state, 'resource', obj)

    async def model_factory(
        self,
        request: fastapi.Request,
        repo: ResourceRepository,
        obj: Any
    ) -> Any:
        assert self.views.create
        if not isinstance(obj, self.views.create):
            raise TypeError(
                f"Can not create a new {self.model.__name__} from "
                f"{type(obj).__name__}"
            )
        # Parse directly from the request JSON content because some
        # fields may be excluded if we would use model_dump().
        try:
            return self.model.model_input(await request.json())
        except pydantic.ValidationError:
            raise
            self.fail(422, f"The object in the request is not a valid {self.model.__name__}.")

    async def on_mutation_request(
        self,
        request: fastapi.Request,
        ctx: IResourceAuthorizationContext,
        repo: IResourceRepository[Any],
        resource: T
    ) -> None:
        """Hook to implement logic prior to mutating a resource."""
        pass

    async def render_to_response(
        self,
        request: fastapi.Request,
        result: T,
        media_type: str | None
    ) -> fastapi.Response:
        headers: dict[str, str] = {}
        if isinstance(result, BaseResource):
            await self.update_cache(request, result) # type: ignore
            headers['ETag'] = result.metadata.resource_version # type: ignore
        if isinstance(result, pydantic.BaseModel):
            result = Response( # type: ignore
                media_type=media_type,
                status_code=self.status_code,
                content=result
            )
        if result is None:
            result = fastapi.Response(status_code=204) # type: ignore
        if not isinstance(result, fastapi.Response):
            raise NotImplementedError
        result.headers.update(headers)
        return result

    async def update_cache(
        self,
        request: fastapi.Request,
        resource: APIResourceType,
        ttl: int | None = None
    ) -> None:
        ttl = ttl or self.ttl
        if ttl is not None and not getattr(request.state, 'cache_lookup', False):
            await self.cache.set(resource.cache_key, resource, ttl=ttl)

    async def __call__(
        self,
        request: fastapi.Request,
        *args: Any, **kwargs: Any
    ) -> fastapi.Response:
        media_type: str | None = getattr(request.state, 'media_type', None)
        repo: ResourceRepository = getattr(request.state, 'resources')
        validator: Validator[Any] | None = getattr(request.state, 'validator', None)
        sig = inspect.signature(self.handle)
        if sig.parameters.get('request'):
            kwargs['request'] = request
        params: dict[str, Any] = {}
        new = None
        for name, value in kwargs.items():
            if name not in sig.parameters:
                continue
            if name in self.input_params:
                value = new = await self.model_factory(request, repo, value)
                if not validator:
                    raise ProgrammingError(
                        "Received input from request but no validator was "
                        f"injected (url: {request.url})"
                    )
                value = await validator.validate(self, new)
            params[name] = value
        try:
            result = await self.handle(**params)
        except Duplicate:
            self.fail(409, "Resource conflict.")
        except (Immutable, ReferentDoesNotExist) as e:
            self.fail(409, e.detail)
        return await self.render_to_response(request, result, media_type=media_type)

    def _get_openapi_responses(self) -> dict[int, Any]:
        responses = self.get_openapi_responses()
        for status_code, response in responses.items():
            headers: dict[str, Any] = response.setdefault('headers', {})
            headers.update(RESPONSE_CONTENT_TYPE)
            if headers.get('Content-Type'):
                headers['Content-Type']['examples'] = [
                    'application/json',
                    'application/yaml'
                ]
            if self.is_detail() and (200 <= status_code < 300):
                headers.update(RESPONSE_ETAG_RESOURCE)

        if not self.authenticated:
            responses.pop(401, None)
            responses.pop(403, None)
        return responses