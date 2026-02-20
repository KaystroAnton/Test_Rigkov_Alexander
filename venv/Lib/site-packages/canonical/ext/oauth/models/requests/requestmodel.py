# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import TypeVar

import httpx
import pydantic

from canonical.lib import FormDataModel
from canonical.ext.oauth.types import Error
from canonical.ext.oauth.types import ProtocolViolation
from canonical.ext.oauth.models.responses import ResponseModel


T = TypeVar('T', bound=ResponseModel)
E = Error | ProtocolViolation


class RequestModel(FormDataModel):
    model_config = {'extra': 'forbid'}

    async def execute(
        self,
        client: httpx.AsyncClient,
        response_model: type[T],
        url: str,
        method: str = 'POST',
    ) -> T | E:
        """Issues a `POST` request using the client to the given
        endpoint `url`.
        """
        adapter: pydantic.TypeAdapter[T | E] = pydantic.TypeAdapter(response_model | E)
        response = await client.request(
            method=method,
            url=url,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            content=self.model_dump_urlencoded()
        )
        return adapter.validate_json(response.content)