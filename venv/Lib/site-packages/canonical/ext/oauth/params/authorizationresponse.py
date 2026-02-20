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

from canonical.ext.oauth.models import responses


AuthorizationResponseDepends = responses.AuthorizationResponse.as_query()
AuthorizationResponse: TypeAlias = Annotated[
    responses.AuthorizationResponse,
    AuthorizationResponseDepends
]