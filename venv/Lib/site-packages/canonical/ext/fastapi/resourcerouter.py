# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
import inspect
from typing import cast
from typing import Any
from typing import Callable
from typing import Generic
from typing import TypeVar
from typing import Unpack

import fastapi
import fastapi.params

from canonical.exceptions import ProgrammingError
from canonical.ext.cache import NullCache
from canonical.ext.api import APIResourceType
from canonical.ext.api import DefaultInspector
from canonical.ext.iam import PermissionQuery
from canonical.ext.iam import PermissionSet
from canonical.ext.iam.protocols import IResourceAuthorizationContext
from canonical.ext.resource import Error
from canonical.lib.protocols import ICache
from canonical.lib.protocols import ICommand
from canonical.utils import merge_signatures
from .apiroute import APIRoute
from .params import AcceptedContentType
from .params import RequestAuthorizationContext
from .response import Response
from . import verbs


C = TypeVar('C')
R = TypeVar('R', bound=APIResourceType)
ResponseModel = TypeVar('ResponseModel')


class ResourceRouterMetaclass(type):

    def __getitem__(cls, model: type[R]) -> type['ResourceRouter[R]']:
        return type(f'{model.__name__}', (cls,), { # type: ignore
            'model': model
        })


class ResourceRouter(fastapi.APIRouter, Generic[R]):
    inspector = DefaultInspector
    detail_verbs: set[str] = {
        'authorize',
        'destroy',
        'exists',
        'get',
        'inspect',
        'replace',
        'update',
    }
    response_class: type[Response[R]]
    resource_model: type[R]

    @classmethod
    def new(cls, model: type[R], **kwargs: Any) -> 'ResourceRouter[R]':
        return cls.typed(model)(**kwargs)

    @classmethod
    def typed(cls, model: type[R]) -> type['ResourceRouter[R]']:
        impl: type[ResourceRouter[R]]  = type(f'{model.__name__}Router', (cls,), {
            'resource_model': model
        })
        return impl

    def __init__(
        self,
        enabled_verbs: set[str] | None = None,
        granter: bool = False,
        **kwargs: Any
    ):
        self.commands_enabled: list[tuple[type[ICommand], str, Callable[..., Any]]] = []
        self.meta = self.inspector.inspect(self.resource_model)
        self.verbs_enabled = set(enabled_verbs or [])
        deps: list[Any] = kwargs.setdefault('dependencies', [])
        deps.extend([
            *self.inject_defaults()
        ])
        self.collect_dependencies(deps, None)
        model = self.resource_model

        super().__init__(route_class=APIRoute, **kwargs)
        self.response_class = Response.typed(model)
        self.resource_model = model
        self.verbs: list[verbs.Verb[Any]] = []

        self.verbs.append(verbs.Exists(self.resource_model))
        if 'create' in self.verbs_enabled:
            self.verbs.append(verbs.DefaultCreate(self.resource_model))

        meta = model.__meta__
        if granter:
            self.add_resource_route(
                method='POST',
                verb='authorize',
                detail=True,
                path=meta.get_url(True, ':permissions'),
                endpoint=self.permissions,
                summary=f'Test {model.__name__} permissions',
                description=(
                    f"Get the permissions granted to the authenticated "
                    f"subject on a specific `{model.__name__}` object."
                ),
                response_model=PermissionSet,
                response_description=f"PermissionSet object.",
                responses={
                    401: {
                        'model': Error,
                        'description': (
                            "The provided request credential is expired, not effective"
                            ", or otherwise malformed."
                        )
                    },
                    403: {
                        'model': Error,
                        'description': "Untrusted credential."
                    },
                },
                authenticated=False,
                with_resource=False
            )
        return

    def add_to_application(
        self,
        app: fastapi.APIRouter,
        register: Callable[..., None],
        tags: list[Any],
        authorization: type[IResourceAuthorizationContext] | None = None,
        cache: ICache = NullCache(),
    ):
        for verb in self.verbs:
            verb.add_to_router(self, register, authorization=authorization, cache=cache)
        tags.append({
            'name': self.resource_model.__name__,
            'description': getattr(self.resource_model, '__doc__', None)
        })

        if self.commands_enabled:
            commands = verbs.Command(self.resource_model)
            for command_class, verb, handler in self.commands_enabled:
                commands.add(command_class, verb, handler)
            commands.add_to_router(self, register, authorization=authorization)
        app.include_router(router=self)

    def add_resource_route(
        self,
        *,
        verb: str,
        method: str,
        path: str,
        summary: str,
        description: str,
        endpoint: Any,
        response_model: type[Any] | None = None,
        response_description: str,
        responses: dict[int, Any] | None = None,
        dependencies: list[Any] | None = None,
        detail: bool = False,
        authenticated: bool = True,
        with_resource: bool = True
    ) -> None:
        model = self.resource_model
        responses = dict(responses or {})
        dependencies = dependencies or []
        if verb in self.detail_verbs:
            detail = True
        if verb in {'create', 'replace', 'update', 'authorize'}:
            dependencies.append(AcceptedContentType({'application/yaml', 'application/json'}))
            responses.update({
                415: {
                    'model': Error,
                    'description': "Invalid content type for request body."
                },
            })
        if detail:
            responses.update({
                404: {
                    'model': Error,
                    'description': (
                        f'The {model.__name__} specified by the path parameter(s) '
                        'does not exist.'
                    )
                }
            })
            #if with_resource:
            #    dependencies.insert(0, self.inject_resource())
        if not authenticated:
            responses.pop(401, None)
        self.add_api_route(
            methods=[method],
            path=path,
            endpoint=endpoint,
            summary=summary,
            description=description,
            responses={**responses},
            response_model=self.resource_model or response_model,
            response_model_by_alias=True,
            response_description=response_description,
            dependencies=[
                fastapi.Depends(self.set_verb(verb)),
                *dependencies,
            ],
            tags=[model.__name__],
        )
        #self.register_resource(path, self.resource_model)

    def add_verb(
        self,
        cls: type[verbs.Verb[Any]],
        authenticated: bool = True,
        ttl: int | None = None,
        **kwargs: Unpack[verbs.VerbParameters]
    ) -> None:
        self.verb_factory(
            cls,
            authenticated=authenticated,
            ttl=ttl,
            **kwargs
        )

    def collect_dependencies(self, dependencies: list[Any], verb: str | None):
        pass

    def command(self, model: type[Any], verb: str) -> Callable[..., Any]:
        model = cast(type[ICommand], model)

        def f(func: Callable[..., Any]) -> Any:
            sig = inspect.signature(func)
            args = list(sig.parameters.values())
            fn = f'{func.__name__}()'
            if len(args) < 2:
                raise TypeError(
                    f"Handler function {fn} must accept "
                    "at least two positional parameters."
                )
            if args[0].default != inspect.Parameter.empty:
                raise TypeError(
                    f'First positional argument to {fn} must not '
                    'have a default.'
                )
            if args[0].annotation != self.resource_model:
                raise TypeError(
                    f'First positional argument to {fn} must be '
                    f'annotated with {self.resource_model.__name__}.'
                )
            if args[1].default != inspect.Parameter.empty:
                raise TypeError(
                    f'Second positional argument to {fn} must not '
                    'have a default.'
                )
            if args[1].annotation != model:
                raise TypeError(
                    f'Second positional argument to {fn} must be '
                    f'annotated with {model.__name__}.'
                )
            if args[1].name != 'command':
                raise TypeError(
                    f'Second positional argument to {fn} must be '
                    f'named \'command\'.'
                )

            h = (model, verb, func)
            if h in self.commands_enabled:
                raise ValueError(
                    f"Handler {fn}() is already registered for command "
                    f"{model.__name__} with verb '{verb}'."
                )
            self.commands_enabled.append(h)
            return func
        return f

    def get_media_type(self, request: fastapi.Request) -> str | None:
        return getattr(request.state, 'media_type', None)

    def inject_defaults(self) -> list[fastapi.params.Depends]:
        return [
            fastapi.params.Depends(self.inject_model),
            fastapi.params.Depends(self.inject_namespace),
        ]

    def inject_model(self, request: fastapi.Request):
        setattr(request.state, 'model', self.resource_model)

    def inject_namespace(self, request: fastapi.Request):
        if 'name' in request.path_params:
            setattr(request.state, 'name', request.path_params['name'])
        if 'namespace' in request.path_params:
            setattr(request.state, 'namespace', request.path_params['namespace'])

    def writer_factory(self, model: type[R], func: Any, partial: bool = False):
        async def f(resource: model, *args: Any, **kwargs: Any) -> Any:
            return await func(resource, *args, **kwargs)
        f.__signature__ = merge_signatures([ # type: ignore
            inspect.signature(func),
            inspect.signature(f)
        ])
        return f

    def set_verb(self, verb: str):
        return self.inject_verb(verb)

    def inject_verb(self, verb: str):
        def f(request: fastapi.Request):
            setattr(request.state, 'verb', verb)
        return f

    def subresource(
        self,
        methods: list[str],
        path: str,
        verb: str,
        **kwargs: Any
    ):
        assert not str.startswith(path, '/')
        path = f'/{self.meta.base_path}/{{name}}/{path}'
        dependencies: list[Any] = kwargs.setdefault('dependencies', [])
        dependencies.insert(0, fastapi.Depends(self.inject_verb(verb)))
        return self.api_route(
            path=path,
            methods=methods,
            tags=[self.resource_model.__name__],
            **kwargs
        )
        
    async def permissions(
        self,
        request: fastapi.Request,
        ctx: RequestAuthorizationContext,
        query: PermissionQuery
    ) -> Response[Any]:
        return self.render_to_response(
            request=request,
            status_code=200,
            instance=PermissionSet.model_validate({
                'granted': await ctx.get_permissions({str(p) for p in query.spec.permissions})
            })
        )

    def render_to_response(
        self,
        *,
        request: fastapi.Request,
        instance: Any,
        status_code: int = 200
    ) -> Response[Any]:
        return Response(
            status_code=status_code,
            media_type=self.get_media_type(request),
            content=instance
        )

    def verb(
        self,
        cls: type[verbs.Verb[Any]],
        *,
        verb: str | None = None,
        authenticated: bool = True,
        ttl: int | None = None,
        **kwargs: Unpack[verbs.VerbParameters]
    ) -> Callable[..., Any]:
        def f(func: Callable[..., Any]) -> Callable[..., Any]:
            sig = inspect.signature(func)
            params = list(sig.parameters.values())
            if not params or params[0].name != 'verb':
                raise ProgrammingError(
                    f"The first argument to {func.__module__}.{func.__name__}() "
                    "must be named 'verb'."
                )

            impl: verbs.Verb[[], Any] = type(cls.__name__, (cls,), { # type: ignore
                'handle': func,
                'verb': verb or getattr(cls, 'verb')
            })
            self.verb_factory(impl, authenticated=authenticated, ttl=ttl, **kwargs) # type: ignore
            return func
        return f

    def verb_factory(self, cls: type[verbs.Verb[Any]], *args: Any, **kwargs: Any):
        if any([v.verb == cls.verb for v in self.verbs]):
            raise ValueError(f"Verb '{cls.verb}' is already declared.")
        self.verbs.append(cls(model=self.resource_model, *args, **kwargs)) # type: ignore
        self.verbs_enabled.add(cls.verb)