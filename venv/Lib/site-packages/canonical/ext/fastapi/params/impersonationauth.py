# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Annotated
from typing import TypeAlias

import fastapi
import httpx

from fastapi.security.utils import get_authorization_scheme_param


class RequestAuthorization(httpx.Auth):

    def __init__(self, request: fastapi.Request):
        authorization = request.headers.get("Authorization")
        self.scheme, self.credentials = get_authorization_scheme_param(authorization)

    async def async_auth_flow(self, request: httpx.Request):
        if self.scheme and self.credentials:
            request.headers['Authorization'] = f'{self.scheme} {self.credentials}'
        yield request


ImpersonationAuth: TypeAlias = Annotated[RequestAuthorization, fastapi.Depends(RequestAuthorization)]