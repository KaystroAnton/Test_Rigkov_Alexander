# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import inspect
from typing import get_args
from typing import get_origin
from typing import Annotated
from typing import Any
from typing import Callable

import fastapi
import fastapi.params

from canonical.ext.cache import NullCache
from canonical.lib.protocols import ICache
from canonical.lib.utils import merge_signatures
from canonical.lib.utils import merged_call


class EndpointRequestHandler:
    _is_coroutine = asyncio.coroutines._is_coroutine # type: ignore

    @property
    def __name__(self) -> str:
        return self.endpoint.__name__

    def __init__(
        self,
        endpoint: type,
        handle: Callable[..., Any],
        cache: ICache = NullCache(),
        **kwargs: Any
    ):
        self.cache = cache
        self.endpoint = endpoint
        self.handle = handle
        self.kwargs = kwargs

        # Check if the asyncio.iscoroutinefunction() call returns
        # True for this object, since it depends on a private
        # symbol.
        assert asyncio.iscoroutinefunction(self) # nosec

        # Inject some parameters that are used by EndpointRequestHandler
        # and Endpoint.
        annotations: dict[str, Any] = {}
        for base in reversed(inspect.getmro(endpoint)):
            annotations.update(inspect.get_annotations(base))
        params: list[inspect.Parameter] = [
            inspect.Parameter(
                kind=inspect.Parameter.POSITIONAL_ONLY,
                name='self_request',
                annotation=fastapi.Request
            )
        ]
        for attname, annotation in annotations.items():
            if get_origin(annotation != Annotated):
                continue
            if len(get_args(annotation)) != 2:
                continue
            annotation, default = get_args(annotation)
            if not isinstance(default, fastapi.params.Depends):
                continue
            params.append(
                inspect.Parameter(
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    name=f'self_{attname}',
                    annotation=annotation,
                    default=default
                )
            )

        # Merge the signatures of the class and the handle method
        # so that they can both receive dependencies.
        self.__signature__ = merge_signatures([
            inspect.signature(endpoint),
            inspect.signature(handle),
        ], extra=params)

    async def __call__(
        self,
        *args: Any,
        **kwargs: Any
    ) -> fastapi.Response:
        attrs = {
            str.lstrip(k, 'self_'): kwargs.pop(k) for k in list(kwargs.keys())
            if str.startswith(k, 'self_')
        }
        endpoint = merged_call(self.endpoint, kwargs)
        endpoint.cache = self.cache
        for attname, value in attrs.items():
            setattr(endpoint, attname, value)
        await endpoint._setup()
        response = await merged_call(self.handle, {**kwargs, 'self': endpoint})
        if response is None:
            response = fastapi.Response(status_code=204)
        return response