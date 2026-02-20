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

from canonical.ext.oauth.types import TokenTypeLiteral
from .grantmodel import GrantModel


class TokenExchangeRequest(GrantModel[Literal['urn:ietf:params:oauth:grant-type:token-exchange']]):
    audience: str | None = pydantic.Field(
        default=None,
        title="Audience",
        description=(
            "The logical name of the target service where the client intends "
            "to use the requested security token. This serves a purpose similar "
            "to the `resource` parameter but with the client providing a "
            "logical name for the target service. An OAuth client identifier, "
            "a SAML entity identifier, and an OpenID Connect Issuer Identifier "
            "are examples of things that might be used as audience parameter "
            "values."
        )
    )

    requested_token_type: TokenTypeLiteral | None = pydantic.Field(
        default=None,
        title="Requested Token Type",
        description=(
            "An identifier for the type of the requested security token. If "
            "the requested type is unspecified, the issued token type is at "
            "the discretion of the authorization server and may be dictated "
            "by knowledge of the requirements of the service or resource "
            "indicated by the resource or audience parameter."
        )
    )

    subject_token: str = pydantic.Field(
        default=...,
        title="Subject Token",
        description=(
            "A security token that represents the identity of the party on "
            "behalf of whom the request is being made. Typically, the subject "
            "of this token will be the subject of the security token issued "
            "in response to the request."
        )
    )

    subject_token_type: TokenTypeLiteral = pydantic.Field(
        default=...,
        title="Subject Token Type",
        description=(
            "An identifier, that indicates the type of the security token "
            "in the `subject_token` parameter."
        )
    )

    actor_token: str | None = pydantic.Field(
        default=None,
        title="Actor Token",
        description=(
            "A security token that represents the identity of the acting party. "
            "Typically, this will be the party that is authorized to use the "
            "requested security token and act on behalf of the subject."
        )
    )

    actor_token_type: TokenTypeLiteral | None = pydantic.Field(
        default=None,
        title="Actor Token Type",
        description=(
            "An identifier, that indicates the type of the security token in the "
            "`actor_token parameter`. This is **required** when the `actor_token` "
            "parameter is present in the request but **must not** be included "
            "otherwise."
        )
    )