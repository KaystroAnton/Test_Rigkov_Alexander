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


class JWTBearerRequest(GrantModel[Literal['urn:ietf:params:oauth:grant-type:jwt-bearer']]):
    assertion: str = pydantic.Field(
        default=...,
        title="Assertion (JWT)",
        description=(
            "A compact encoded JSON Web Token (JWT).\n\n"
            "The value of the `assertion` parameter **must** "
            "contain a single JWT."
        )
    )

    scope: str | None = pydantic.Field(
        default=None,
        title="Scope",
        description=(
            "The scope of the access request."
        )
    )