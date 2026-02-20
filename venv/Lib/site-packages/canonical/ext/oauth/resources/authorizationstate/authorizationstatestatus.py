# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from canonical.ext.api import ResourceStatus


class AuthorizationRequestStateStatus(ResourceStatus):
    code: str | None = pydantic.Field(
        default=None,
        alias='authorizationCode',
        title="Authorization Code",
        description=(
            "The authorization code that may be used to obtain an "
            "access token from the token endpoint."
        )
    )
    access_token: str | None = pydantic.Field(
        default=None,
        alias='accessToken',
        title="Access Token",
        description=(
            "For proxying and obtaining states, the access token received "
            "from the authorization server.\n\nFor issuing states, the "
            "issued access token."
        )
    )

    refresh_token: str | None = pydantic.Field(
        default=None,
        title="Refresh Token",
        alias='refreshToken',
        description=(
            "For proxying and obtaining states, the refresh token received "
            "from the authorization server.\n\nFor issuing states, the "
            "issued refresh token."
        )
    )