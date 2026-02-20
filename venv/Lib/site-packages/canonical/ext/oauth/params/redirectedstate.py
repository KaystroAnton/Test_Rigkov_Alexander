# Copyright (C) 2023-2024 Cochise Ruhulessin
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

from canonical.ext.fastapi.params import HTTPClient
from canonical.ext.fastapi.params import ResourceRepository
from canonical.ext.oauth.models.responses import AuthorizationResponse
from canonical.ext.oauth.resources import AuthorizationState
from canonical.ext.oauth.types import StopSnooping
from canonical.ext.oauth import ClusterClient


async def get(
    http: HTTPClient,
    repo: ResourceRepository,
    params: AuthorizationResponse = AuthorizationResponse.as_query()
):
    if not params.state or not params.code:
        raise NotImplementedError
    try:
        state = await repo.get(params.state, AuthorizationState, require=True)
    except repo.DoesNotExist as e:
        raise StopSnooping from e
    ctrl = state.get_controller(require=True, model=ClusterClient)
    client = await repo.get(ctrl)
    await state.obtain(http, client.spec, params)
    yield state


RedirectedState: TypeAlias = Annotated[
    AuthorizationState,
    fastapi.Depends(get)
]

