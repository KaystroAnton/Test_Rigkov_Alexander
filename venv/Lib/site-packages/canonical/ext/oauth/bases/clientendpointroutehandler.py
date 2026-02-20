# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import json
import urllib.parse
from typing import Any
from typing import Callable
from typing import Coroutine

import fastapi
import fastapi.routing
import starlette.responses

from canonical.ext.oauth.utils import DefaultMediaTypeSelector


class ClientEndpointRouteHandler(fastapi.routing.APIRoute):

    class request_class(fastapi.Request):
        selector = DefaultMediaTypeSelector
        # TODO: We accept both form data and JSON, but fastapi.Form and
        # pydantic models don't work well together. Thus, for requests
        # with form data, the json() method should also parse the
        # form data. TODO: This will break if FastAPI to decides to parse
        # the data and inject dependencies based on the Content-Type
        # header.

        async def body(self) -> bytes:
            if not hasattr(self, "_body"):
                chunks: list[bytes] = []
                async for chunk in self.stream():
                    chunks.append(chunk)
                self._body = b"".join(chunks)
                mt = self.selector.select(self.headers.get('Content-Type'))
                if mt == "application/x-www-form-urlencoded":
                    # TODO: Check charset
                    self._headers = self._headers.mutablecopy()
                    self._headers['Content-Type'] = "application/json"
                    data = dict(urllib.parse.parse_qsl(bytes.decode(self._body)))
                    self._body = str.encode(json.dumps(data))
            return self._body

    def get_route_handler(self) -> Callable[[fastapi.Request], Coroutine[Any, Any, starlette.responses.Response]]:
        handler = super().get_route_handler()

        async def f(request: fastapi.Request) -> starlette.responses.Response:
            request = self.request_class(request.scope, request.receive)

            return await handler(request)

        return f