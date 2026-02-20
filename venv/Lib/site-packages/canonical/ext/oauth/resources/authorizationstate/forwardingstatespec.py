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

import pydantic

from canonical.ext.api.objectmeta import ObjectMeta
from canonical.ext.oauth.models.responses import TokenResponse
from canonical.ext.oauth.types import RedirectURI
from canonical.lib.types import HTTPResourceLocator
from .authorizationstatespec import AuthorizationStateSpec


class ForwardingStateSpec(AuthorizationStateSpec[Literal['forwarding']]):
    forward_url: HTTPResourceLocator = pydantic.Field(
        default=...,
        alias='forwardUrl',
        title="Forward URL",
        description=(
            "The URL to which the user agent must be redirected after "
            "obtaining the grant."
        )
    )

    def get_redirect_uri(self) -> RedirectURI | None:
        raise NotImplementedError

    def get_return_url(self, code: str, iss: str | None = None) -> str:
        return self.forward_url.with_query(state=self.params.state)

    def get_user_agent_redirect_uri(
        self,
        metadata: ObjectMeta[str]
    ) -> str:
        return self.params.authorize(self.authorization_endpoint)


    def on_obtained(self, response: TokenResponse) -> dict[str, Any]:
        raise NotImplementedError