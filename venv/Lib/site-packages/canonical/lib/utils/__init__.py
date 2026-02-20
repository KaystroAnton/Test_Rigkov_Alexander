# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import inspect
import operator
from collections import abc
from collections import OrderedDict
from functools import reduce
from itertools import chain
from typing import Any
from typing import Callable

from ._deephash import deephash
from .deferred import Deferred
from .loader import import_symbol


__all__: list[str] = [
    'deephash',
    'import_symbol',
    'Deferred',
]


class class_property:
    __module__: str = 'oauthx.utils'

    def __init__(self, func: Callable[..., Any]):
        self.func = func

    def __get__(self, instance: Any, cls: Any) -> Any:
        return self.func(cls)


def merge_signatures(
    signatures: list[inspect.Signature],
    extra: list[inspect.Parameter] | None = None
) -> inspect.Signature:
    """Merge signatures to that FastAPI can inject the dependencies."""
    extra = extra or []
    params: dict[str, inspect.Parameter] = OrderedDict()
    for param in chain(chain(*[x.parameters.values() for x in signatures]), extra):
        if param.name in {'self', 'cls'}:
            continue
        if param.name.startswith('_'):
            continue
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            continue
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            continue
        params[param.name] = param

    return signatures[0].replace(
        parameters=list(sorted(params.values(), key=lambda p: (p.kind, p.default != inspect._empty))) # type: ignore
    )


def merged_call(func: Callable[..., Any], kwargs: Any) -> Any:
    sig = inspect.signature(func)
    return func(**{k: v for k, v in kwargs.items() if k in sig.parameters})


def throw(cls: type[Exception], *args: Any, **kwargs: Any):
    raise cls(*args, **kwargs)


def jsonpath(mapping: abc.Mapping[str, Any], path: str) -> Any:
    if not str.startswith(path, '/'):
        raise ValueError("Path must start with a slash.")
    parts: list[str] = []
    for p in str.split(str.lstrip(path, '/'), '/'):
        p = p.replace('~0', '~')
        p = p.replace('~1', '/')
        parts.append(p)
    return reduce(operator.getitem, parts, mapping)
    