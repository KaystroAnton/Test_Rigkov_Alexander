# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal

import pydantic

from canonical.ext.oauth.types import RedirectURI
from .grantmodel import GrantModel


class AuthorizationCodeRequest(GrantModel[Literal['authorization_code']]):
    code: str = pydantic.Field(
        default=...,
        title="Authorization Code",
        description=(
            "The authorization code received from the authorization server."
        )
    )

    redirect_uri: RedirectURI | None = pydantic.Field(
        default=None,
        title="Redirect URI",
        description=(
            "Required, if the `redirect_uri` parameter was included in the "
            "authorization request, and their values **must** be identical."
        )
    )