# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging
from typing import Any
from typing import Callable
from typing import Coroutine

import fastapi
import fastapi.params
import fastapi.routing
import pydantic
from fastapi.dependencies.utils import get_parameterless_sub_dependant
from fastapi.exceptions import HTTPException
from starlette.routing import request_response # type: ignore

from canonical.ext.resource import Error
from canonical.utils.http import MediaTypeSelector
from .response import Response


class APIRoute(fastapi.routing.APIRoute):
    logger: logging.Logger = logging.getLogger('uvicorn')
    media_types: MediaTypeSelector = MediaTypeSelector({
        'text/html',
        'application/json',
        'application/yaml'
    })

    def inject(
        self,
        dependency: fastapi.params.Depends,
        index: int = -1
    ) -> None:
        dependant = get_parameterless_sub_dependant(
            depends=dependency,
            path=self.path_format
        )
        self.dependant.dependencies.insert(0, dependant)
        self.app = request_response(self.get_route_handler())

    def get_route_handler(self) -> Callable[[fastapi.Request], Coroutine[Any, Any, fastapi.Response]]:
        handler = super().get_route_handler()

        async def f(request: fastapi.Request) -> fastapi.Response:
            response: Response[Any]
            try:
                response = await handler(request) # type: ignore
            except pydantic.ValidationError as e:
                # TODO: This should normally be a validation error, but some in
                # some implementations, FastAPI does not catch the validation
                # error (see QueryModelMixin).
                errors: list[dict[str, Any]] = list([dict(x) for x in e.errors()])
                field_errors: list[dict[str, Any]] = []
                if not any([x.get('type') == 'extra_forbidden' for x in errors]):
                    raise
                for error in errors:
                    field_errors.append({
                        'message': error['msg'],
                        'schema_path': tuple(error['loc'] or []),
                        'type': error['type'],
                        'data': error['input']
                    })
                assert request.client
                response = Response(
                    media_type=self.media_types.select(request.headers.get('Accept')),
                    status_code=422,
                    content=Error.factory({
                        'detail': "Illegal additional inputs.",
                        'request': {
                            'url': str(request.url),
                            'host': request.client.host,
                        },
                        'fieldErrors': field_errors,
                        'status_code': 422,
                    })
                )
            except fastapi.exceptions.RequestValidationError as e:
                # TODO: Create a decent error handler.
                errors: list[dict[str, Any]] = list(e.errors())
                status_code: int | None = None
                detail: str | None = None
                field_errors: list[dict[str, Any]] = []
                while errors:
                    error = errors.pop()
                    location, *fields = error.get('loc') or [None]
                    if location is None:
                        raise
                    if location in {'body', 'query'} and fields:
                        status_code = 422
                        field_errors.append({
                            'message': error['msg'],
                            'schema_path': tuple(fields),
                            'type': error['type'],
                            'data': error['input']
                        })
                        continue
                    if location == 'path':
                        # Validation errors in the path should simple return a 404,
                        # because the resource does not exist.
                        status_code = 404
                        break
                    if status_code not in {None, 422}:
                        raise
                assert status_code is not None, e
                assert request.client
                response = Response(
                    media_type=self.media_types.select(request.headers.get('Accept')),
                    status_code=status_code,
                    content=Error.factory({
                        'detail': detail or 'No detailed message provided.',
                        'request': {
                            'url': str(request.url),
                            'host': request.client.host,
                        },
                        'fieldErrors': field_errors,
                        'status_code': status_code,
                    })
                )
            except NotImplementedError as e:
                # TODO: Implement a switch to change the loglevel.
                self.logger.exception("Client requested a feature that was not implemented.")
                assert request.client
                response = Response(
                    media_type=self.media_types.select(request.headers.get('Accept')),
                    status_code=422,
                    content=Error.factory({
                        'detail': "The requested feature is not implemented by the server.",
                        'request': {
                            'url': str(request.url),
                            'host': request.client.host,
                        },
                        'status_code': 422,
                    })
                )
            except HTTPException as e:
                assert request.client
                response = Response(
                    media_type=self.media_types.select(request.headers.get('Accept')),
                    status_code=e.status_code,
                    content=Error.factory({
                        'detail': e.detail,
                        'request': {
                            'url': str(request.url),
                            'host': request.client.host,
                        },
                        'status_code': e.status_code,
                    })
                )
            except Exception as e:
                self.logger.exception("Caught fatal exception.")
                assert request.client
                response = Response(
                    media_type=self.media_types.select(request.headers.get('Accept')),
                    status_code=500,
                    content=Error.factory({
                        'detail': (
                            "The server encountered an unexpected condition "
                            "that prevented it from fulfilling the request."
                        ),
                        'request': {
                            'url': str(request.url),
                            'host': request.client.host,
                        },
                        'status_code': 500,
                    })
                )
            if request.method == 'HEAD':
                # Remove the body from HEAD requests.
                response = Response(
                    status_code=response.status_code,
                    headers=response.headers,
                    media_type=response.media_type,
                )
            return response
        return f