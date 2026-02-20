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
from typing import Any
from typing import Callable

import fastapi


class Endpoint:
    _is_coroutine = asyncio.coroutines._is_coroutine # type: ignore

    @property
    def __name__(self) -> str:
        return self.name

    def __init__(
        self,
        name: str,
        signature: inspect.Signature,
        handle: Callable[..., Any],
    ):
        self.handle = handle
        self.name = name
        self.__signature__ = signature
        # Check if the asyncio.iscoroutinefunction() call returns
        # True for this object, since it depends on a private
        # symbol.
        assert asyncio.iscoroutinefunction(self) # nosec

    async def __call__(self, *args: Any, **kwargs: Any) -> fastapi.Response:
        response = await self.handle(*args, **kwargs)
        if inspect.isawaitable(response):
            response = await response
        assert isinstance(response, fastapi.Response)
        return response