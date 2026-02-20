# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import inspect
from collections import OrderedDict
from collections.abc import MutableMapping
from typing import Any
from typing import Callable
from typing import Generator

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


def merge_signatures(signatures: list[inspect.Signature]) -> inspect.Signature:
    """Merge signatures to that FastAPI can inject the dependencies."""
    params: dict[str, inspect.Parameter] = OrderedDict()
    for sig in signatures:
        for param in sig.parameters.values():
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


def throw(cls: type[Exception], *args: Any, **kwargs: Any):
    raise cls(*args, **kwargs)