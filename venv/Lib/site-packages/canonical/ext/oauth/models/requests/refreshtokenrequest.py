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

from .grantmodel import GrantModel


class RefreshTokenRequest(GrantModel[Literal['refresh_token']]):
    refresh_token: str = pydantic.Field(
        default=...,
        title="Refresh Token",
        description=(
            "The refresh token issued to the client."
        )
    )

    scope: str | None = pydantic.Field(
        default=None,
        title="Scope",
        description=(
            "The scope of the access request. The requested scope **must not** "
            "include any scope not originally granted by the resource owner, "
            "and if omitted is treated as equal to the scope originally granted "
            "by the resource owner."
        )
    )