# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable
from typing import Coroutine

import fastapi
import fastapi.routing
import starlette.responses

from canonical.ext.templates import TemplateService
from canonical.ext.oauth.types import StopSnooping
from canonical.ext.oauth.types import UserAgentException


class UserAgentRouteHandler(fastapi.routing.APIRoute):

    def get_route_handler(self) -> Callable[[fastapi.Request], Coroutine[Any, Any, starlette.responses.Response]]:
        handler = super().get_route_handler()

        async def f(request: fastapi.Request) -> starlette.responses.Response:
            templates = TemplateService(
                request=request,
                packages=['canonical.ext.oauth']
            )
            setattr(request.state, 'templates', templates)
            try:
                response = await handler(request)
            except (UserAgentException, StopSnooping) as e:
                response = await e.render(templates)
            return response
        return f