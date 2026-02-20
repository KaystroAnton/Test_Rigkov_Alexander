# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Generic
from typing import Literal
from typing import TypeVar

import pydantic

from canonical.ext.oauth.types import AuthenticationMethod
from .requestmodel import RequestModel


G = TypeVar('G')
ClientAssertionType = Literal[
    'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'
]

RFC7523 = 'https://datatracker.ietf.org/doc/html/rfc7523'


class GrantModel(RequestModel, Generic[G]):
    grant_type: G = pydantic.Field(
        default=...,
        title="Grant Type",
        description=(
            "Specifies the grant type requested by the client."
        )
    )

    client_id: str | None = pydantic.Field(
        default=None,
        title="Client ID",
        description=(
            "Required, if the client is not authenticating with "
            "the authorization server or authentication is required "
            "and the client uses the `client_secret_post` method."
        )
    )

    client_secret: str | None = pydantic.Field(
        default=None,
        title="Client Secret",
        description=(
            "Required if the client is authenticating with the "
            "`client_secret_post` method. The client may omit "
            "the parameter if the client secret is an empty "
            "string"
        ),
    )

    client_assertion_type: ClientAssertionType | None = pydantic.Field(
        default=None,
        title="Client Assertion Type",
        description=(
            "The format of the assertion as defined by the authorization "
            "server. The value is an absolute URI. If `client_assertion_"
            "type` is provided, then `client_secret` **must** be omitted."
            
        )
    )

    client_assertion: str | None = pydantic.Field(
        default=None,
        title="Client Assertion",
        description=(
            "The client assertion in the format and encoding indicated "
            "by the `client_assertion_type` field.\n\n"
            "This server supports the following assertion types:\n\n"
            "- `urn:ietf:params:oauth:client-assertion-type:jwt-bearer` - A "
            "JSON Web Token (JWT) signed by a trusted issuer that holds the "
            f"claims identifying the client. Refer to (RFC7523)[{RFC7523}] "
            "for a complete description of the claims and their meanings."
        )
    )

    resource: list[str] = pydantic.Field(
        default_factory=list,
        title="Resources",
        description=(
            "Indicates the target service or protected resource "
            "where the client intends to use the requested access token."
        )
    )

    def assert_client(self, type: ClientAssertionType, assertion: str):
        self.client_id = self.client_secret = None
        self.client_assertion_type = type
        self.client_assertion = assertion

    def identify(self, client_id: str) -> None:
        self.client_id = client_id

    def set_client_secret(self, mode: AuthenticationMethod, secret: str) -> None:
        if mode != 'client_secret_post':
            raise NotImplementedError
        self.client_secret = secret