# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import logging
import inspect
from typing import cast
from typing import Callable
from typing import TypeVar
from typing import Unpack

import httpx
import pydantic
from httpx._types import URLTypes

from canonical.lib.utils.http import MediaTypeSelector
from .asyncclientparams import AsyncClientParams
from .asyncrequestparams import AsyncRequestParams
from .response import Response


__all__: list[str] = [
    'AsyncClient',
    'AsyncClientParams',
]


T = TypeVar('T')


class AsyncClient(httpx.AsyncClient):
    logger: logging.Logger = logging.getLogger('headless')

    @property
    def domain(self) -> str:
        return self.base_url.netloc.decode()

    def can_retry_timeout(self, request: httpx.Request):
        return request.method in {'GET', 'HEAD', 'OPTIONS'}

    async def request(
        self,
        method: str,
        url: URLTypes,
        *,
        response_model: type[T] | Callable[[bytes], T] = bytes,
        **kwargs: Unpack[AsyncRequestParams]
    ) -> Response[T]:
        abort = False
        attempts: int = 0
        counter = -1
        delay: int = 5
        exception = None
        while True:
            attempts += 1
            if counter > 0:
                counter -= 1
            must_log = (attempts % 3 == 0) or (counter != -1)
            try:
                response = await super().request(method, url, **kwargs)
                response.raise_for_status()
                break
            except httpx.ConnectError as e:
                # Assumption is that there is no internet connection.
                if must_log:
                    self.logger.warning("Network issues prevent request (url: %s)", e.request.url)
                await asyncio.sleep(delay)
                continue
            except httpx.ConnectTimeout as e:
                # A connection timeout may occur due to intermediary issues, or
                # a booting application that has not bound its port yet.
                if must_log:
                    self.logger.warning("Connection timeout (url: %s)", e.request.url)
                await asyncio.sleep(delay)
                continue
            except httpx.ReadTimeout as e:
                # A read timeout means that we've succesfully connected, but there
                # was a timeout reading the response. This should only be retried on
                # safe HTTP methods, because we do not know what actually caused the
                # timeout, thus any destructive operations may actually have been
                # completed succesfully.
                self.logger.warning("Caught timeout (url: %s).", e.request.url)
                if not self.can_retry_timeout(e.request):
                    raise
                await asyncio.sleep(delay)
                continue
            except httpx.HTTPStatusError as e:
                if e.response.status_code != 429:
                    response = e.response
                    break
                if must_log:
                    self.logger.warning("Request was rate-limited (url: %s)", e.response.url)
                await asyncio.sleep(delay)
            except httpx.RemoteProtocolError as e:
                # This is an edge condition where we might try to make a
                # request to a server that closed it ports. There are
                # other reasons, so we limit the amount of retries.
                if counter == -1:
                    counter = 3
                if must_log:
                    self.logger.warning("Remote protocol violation (url: %s)", e.request.url)
                exception = e
                await asyncio.sleep(delay)
            if counter == 0:
                abort = True
            if abort and exception:
                raise exception

        selector = MediaTypeSelector({'application/json'})
        if response.status_code >= 200:
            media_type = selector.select(response.headers.get('Content-Type'))
            if media_type == 'application/json':
                setattr(response, 'result', response.content)
                if inspect.isclass(response_model)\
                and issubclass(response_model, pydantic.BaseModel):
                    setattr(response, 'result', response_model.model_validate(response.json()))

        return cast(Response[T], response)