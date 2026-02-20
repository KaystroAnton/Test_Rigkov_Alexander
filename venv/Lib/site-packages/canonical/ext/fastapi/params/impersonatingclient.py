# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from ..resourceclient import ResourceClient
from .impersonationauth import ImpersonationAuth


def ImpersonatingClient(key:str, base_url: str):
    async def f(auth: ImpersonationAuth, request: fastapi.Request):
        async with ResourceClient(auth=auth, base_url=base_url) as client:
            setattr(request.state, key, client)
            yield client
    return fastapi.Depends(f)