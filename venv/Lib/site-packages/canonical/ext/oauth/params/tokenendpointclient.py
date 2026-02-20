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

import fastapi
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials

from canonical.ext.oauth.models import ClientAssertion
from canonical.ext.oauth.protocols import IRegisteredClient
from canonical.ext.oauth.security import RFC7521
from .tokenrequest import TokenRequest


basic = HTTPBasic(
    auto_error=False,
    description=(
        "Clients in possession of a client password **may** use the HTTP Basic "
        "authentication scheme as defined in RFC 2617 to authenticate with the "
        "authorization server.\n\n"
        "If the client registered a JSON Web Key Set (JWKS) holding it's "
        "public keys, then it **should** use the RFC 7521 Client Assertion "
        "method using a JWT client assertion, even if it also has a client "
        "secret configured."
    ),
    scheme_name='Client Secret (HTTP Basic Auth)'
)

client_assertion = RFC7521(
    description=(
        "An assertion is a package of information that facilitates "
        "the sharing of identity and security information across "
        "security domains. Through the RFC 7521 Assertion Framework "
        "for OAuth 2.0 Client Authentication and Authorization Grants, "
        "clients can employ various mechanisms to authenticate them"
        "selves.\n\nThis server supports the following methods:"
    ),
    scheme_name='RFC 7521 Client Assertion'
)


async def get(
    params: TokenRequest,
    credentials: HTTPBasicCredentials | None = fastapi.Depends(basic),
    assertion: ClientAssertion | None = fastapi.Depends(client_assertion),
) -> str | None:
    if not any([params.client_id, credentials, assertion]):
        # TODO
        raise NotImplementedError
    return 'foo'


TokenEndpointClientDepends = fastapi.Depends(get)
TokenEndpointClient: TypeAlias = Annotated[IRegisteredClient, TokenEndpointClientDepends]