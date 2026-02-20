# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import inspect
from collections import OrderedDict
from typing import get_origin
from typing import Any
from typing import Annotated
from typing import Callable

import fastapi
import fastapi.params

from canonical.exceptions import ProgrammingError


__all__: list[str] = [
    'request_state'
]


UNSET = object()


def request_state(
    name: str,
    annotation: Any,
    required: bool = True,
    default: object = UNSET
) -> Any:
    if not bool(default != UNSET) ^ bool(required):
        raise TypeError(
            "The `required` and `default` parameters are mutually "
            "exclusive."
        )

    def f(request: fastapi.Request):
        v = getattr(request, name, default)
        if v == UNSET and required:
            raise ProgrammingError(
                f"Dependency requires request.state.{name} "
                "to be present."
            )
        setattr(request.state, name, v)
        return v

    return fastapi.Depends(f)


def inject_state(name: str, required: bool = True) -> Any:
    def f(request: fastapi.Request):
        try:
            return getattr(request.state, name)
        except AttributeError:
            if required:
                raise ProgrammingError(
                    f"Dependency {name} is requested from the request state "
                    "but it was not injected."
                )
            return None
    return fastapi.Depends(f)


def update_signature(f: Callable[..., Any], *args: Any, **kwargs: Any):
    sig = inspect.signature(f)
    params: OrderedDict[str, inspect.Parameter] = OrderedDict()
    if 'request' in sig.parameters:
        params['request'] = sig.parameters['request']
    for i, dependency in enumerate(args):
        name = f'__arg_{i}'
        if isinstance(dependency, fastapi.params.Depends):
            kwargs[name] = dependency
            continue
        if not get_origin(dependency) == Annotated:
            continue
        params[name] = inspect.Parameter(
            kind=inspect.Parameter.POSITIONAL_ONLY,
            name=name,
            annotation=dependency
        )
        
    for name, dependency in kwargs.items():
        if not isinstance(dependency, fastapi.params.Depends):
            if not callable(dependency):
                dependency = lambda: dependency
            dependency = fastapi.params.Depends(dependency)
        params[name] = inspect.Parameter(
            kind=inspect.Parameter.KEYWORD_ONLY,
            name=name,
            default=dependency,
            annotation=Any
        )
    sig = sig.replace(parameters=list(params.values()))
    return setattr(f, '__signature__', sig)


def inject(*args: Any, **kwargs: Any):
    def f(request: fastapi.Request, **kwargs: Any):
        for k, v in kwargs.items():
            setattr(request.state, k, v)

    update_signature(f, *args, **kwargs)
    return [fastapi.Depends(f)]


def requires(
    dependant: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    def f(**params: Any):
        args: list[Any] = []
        kwargs: dict[str, Any] = {}
        for k, v in sorted(params.items(), key=lambda x: x[0]):
            if k.startswith('__arg'):
                args.append(v)
                continue
            kwargs[k] = v
        return dependant(*args, **kwargs)

    update_signature(f, *args, **kwargs)
    return fastapi.Depends(f)