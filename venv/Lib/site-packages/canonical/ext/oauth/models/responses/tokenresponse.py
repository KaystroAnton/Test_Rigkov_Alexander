# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .responsemodel import ResponseModel


class TokenResponse(ResponseModel):
    access_token: str = pydantic.Field(
        default=...,
        title="Access Token",
        description=(
            "The access token issued by the authorization server."
        )
    )

    token_type: str = pydantic.Field(
        default=...,
        title="Token Type",
        description=(
            "The type of the token issue. Value is case insensitive."
        )
    )

    expires_in: int | None = pydantic.Field(
        default=None,
        title="Time-to-Live",
        description=(
            "The lifetime in seconds of the access token.  For example, the "
            "value `3600` denotes that the access token will expire in one "
            "hour from the time the response was generated."
        )
    )

    refresh_token: str | None = pydantic.Field(
        default=None,
        title="Refresh Token",
        description=(
            "The refresh token, which can be used to obtain new access "
            "tokens using the same authorization grant"
        )
    )

    scope: str | None = pydantic.Field(
        default=None,
        title="Scope",
        description=(
            "Optional, if identical to the scope requested by the client; "
            "otherwise, required."
        )
    )

    state: str | None = pydantic.Field(
        default=None,
        title="State",
        description=(
            "Required if the `state` parameter was present in the client "
            "authorization request. The exact value received from the "
            "client."
        )
    )