# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal

from canonical.ext.oauth.models.responses import TokenResponse
from canonical.ext.oauth.types import RedirectURI
from .authorizationstatespec import AuthorizationStateSpec


class ObtainingStateSpec(AuthorizationStateSpec[Literal['obtaining']]):

    def get_redirect_uri(self) -> RedirectURI | None:
        raise NotImplementedError

    def on_obtained(self, response: TokenResponse) -> dict[str, Any]:
        raise NotImplementedError