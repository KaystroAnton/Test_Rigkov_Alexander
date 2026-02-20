# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`ServerMetadata`."""
import httpx
import pydantic

from canonical.lib.types import HTTPResourceLocator


class ServerMetadata(pydantic.BaseModel):
    model_config = {'populate_by_name': True}

    issuer: HTTPResourceLocator = pydantic.Field(
        default=...,
        title="Issuer",
        description="Authorization server's issuer identifier URL.",
    )

    authorization_endpoint: HTTPResourceLocator | None = pydantic.Field(
        default=None,
        title="Authorization endpoint",
        alias='authorizationEndpoint',
        description="URL of the authorization server's authorization endpoint.",
    )

    token_endpoint: str = pydantic.Field(
        default=...,
        title="Token endpoint",
        alias='tokenEndpoint',
        description="URL of the authorization server's token endpoint.",
    )

    jwks_uri: str | None = pydantic.Field(
        default=None,
        title="JSON Web Key Set (JWKS) URI",
        alias='jwksUri',
        description="URL of the authorization server's JWK Set document.",
    )

    registration_endpoint: str | None = pydantic.Field(
        default=None,
        title="Registration endpoint",
        alias='registrationEndpoint',
        description=(
            "URL of the authorization server's **OAuth 2.0 Dynamic Client "
            "Registration Endpoint**."
        ),
    )

    scopes_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported scopes",
        description=(
            "JSON array containing a list of the OAuth 2.0 `scope` values that "
            "this authorization server supports."
        ),
    )

    response_types_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported response types",
        description=(
            "JSON array containing a list of the OAuth 2.0 `response_type` "
            "values that this authorization server supports."
        ),
    )

    response_modes_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported response modes",
        description=(
            "JSON array containing a list of the OAuth 2.0 `response_mode` "
            "values that this authorization server supports."
        ),
    )

    grant_types_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported grant types",
        description=(
            "JSON array containing a list of the OAuth 2.0 `grant_types` "
            "values that this authorization server supports."
        ),
    )

    token_endpoint_auth_methods_supported: list[str] = pydantic.Field(
        default=[],
        title="Supported client authentication methods",
        description=(
            "JSON array containing a list of client authentication methods "
            "supported by this token endpoint."
        ),
    )

    token_endpoint_auth_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the token endpoint for the signature on the JWT "
            "used to authenticate the client at the token endpoint."
        ),
    )

    service_documentation: str | None = pydantic.Field(
        default=None,
        title="Documentation",
        description=(
            "URL of a page containing human-readable information that "
            "developers might want or need to know when using the "
            "authorization server."
        ),
    )

    ui_locales_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported locals for UI",
        description=(
            "Languages and scripts supported for the user interface, "
            "represented as a JSON array of language tag values from BCP 47."
        ),
    )

    op_policy_uri: str | None= pydantic.Field(
        default=None,
        title="Data policy URL",
        description=(
            "URL that the authorization server provides to the person "
            "registering the client to read about the authorization server's "
            "requirements on how the client can use the data provided by the "
            "authorization server."
        ),
    )

    op_tos_uri: str | None= pydantic.Field(
        default=None,
        title="Terms of service URL",
        description=(
            "URL that the authorization server provides to the person "
            "registering the client to read about the authorization server's "
            "terms of service."
        ),
    )

    revocation_endpoint: str | None = pydantic.Field(
        default=None,
        title="Revocation endpoint",
        description="URL of the authorization server's revocation endpoint.",
    )

    revocation_endpoint_auth_methods_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported authentication methods",
        description=(
            "JSON array containing a list of client authentication methods "
            "supported by this revocation endpoint."
        ),
    )

    revocation_endpoint_auth_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the revocation endpoint for the signature on the JWT "
            "used to authenticate the client at the revocation endpoint."
        ),
    )

    introspection_endpoint: str | None = pydantic.Field(
        default=None,
        title="Introspection endpoint",
        description="URL of the authorization server's introspection endpoint.",
    )

    introspection_endpoint_auth_methods_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported authentication methods",
        description=(
            "JSON array containing a list of client authentication methods "
            "supported by this introspection endpoint."
        ),
    )

    introspection_endpoint_auth_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the introspection endpoint for the signature on the JWT "
            "used to authenticate the client at the introspection endpoint."
        ),
    )

    signed_metadata: str | None = pydantic.Field(
        default=None,
        title="Signed metadata",
        description=(
            "Signed JWT containing metadata values about the authorization "
            "server as claims."
        )
    )

    device_authorization_endpoint: str | None = pydantic.Field(
        default=None,
        title="Device authorization endpoint",
        description=(
            "URL of the authorization server's device authorization endpoint."
        ),
    )

    tls_client_certificate_bound_access_tokens: bool | None = pydantic.Field(
        default=True,
        title="Supports mTLS certificate-bound access tokens",
        description=(
            "Indicates authorization server support for mutual-TLS client "
            "certificate-bound access tokens."
        ),
    )

    mtls_endpoint_aliases: dict[str, str] | None = pydantic.Field(
        default={},
        title="Alternative mTLS endpoints",
        description=(
            "JSON object containing alternative authorization server "
            "endpoints, which a client intending to do mutual TLS will "
            "use in preference to the conventional endpoints."
        ),
    )

    nfv_token_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as NFV Token."
        ),
    )

    nfv_token_encryption_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "NFV Token."
        ),
    )

    nfv_token_encryption_enc_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "NFV Token."
        ),
    )

    userinfo_endpoint: str | None = pydantic.Field(
        default=None,
        title="UserInfo endpoint",
        description="URL of the authorization servers' UserInfo Endpoint.",
    )

    acr_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported ACR",
        description=(
            "JSON array containing a list of the Authentication Context Class "
            "References that this authorization server supports."
        ),
    )

    subject_types_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported subject types",
        description=(
            "JSON array containing a list of the Subject Identifier types that "
            "this authorization server supports"
        ),
    )

    id_token_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as ID Token."
        ),
    )

    id_token_encryption_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "ID Token."
        ),
    )

    id_token_encryption_enc_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "ID Token."
        ),
    )

    userinfo_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as UserInfo Endpoint."
        ),
    )

    userinfo_encryption_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "UserInfo Endpoint."
        ),
    )

    userinfo_encryption_enc_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "UserInfo Endpoint."
        ),
    )

    request_object_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of the JWS signing algorithms "
            "supported by the server for signing the JWT used as Request Object."
        ),
    )

    request_object_encryption_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`alg` values) supported by the server to encode the JWT used as "
            "Request Object."
        ),
    )

    request_object_encryption_enc_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the server to encode the JWT used as "
            "Request Object."
        ),
    )

    display_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported display modes",
        description=(
            "JSON array containing a list of the `display` parameter values "
            "that the OpenID Provider supports."
        ),
    )

    claim_types_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported Claims Types",
        description=(
            "JSON array containing a list of the Claims Types "
            "that the OpenID Provider supports."
        )
    )

    claims_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported Claims Types",
        description=(
            "JSON array containing a list of the Claim Names of the Claims "
            "that the OpenID Provider MAY be able to supply values for."
        )
    )

    claims_locales_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported claim locales",
        description=(
            "Languages and scripts supported for values in Claims being "
            "returned, represented as a JSON array of BCP 47."
        ),
    )

    claims_parameter_supported: bool | None = pydantic.Field(
        default=False,
        title="Supports `claims` parameter?",
        description=(
            "Boolean value specifying whether the OP supports use of the "
            "`claims` parameter."
        ),
    )

    request_parameter_supported: bool | None = pydantic.Field(
        default=False,
        title="Supports `request` parameter?",
        description=(
            "Boolean value specifying whether the OP supports use of the "
            "`request` parameter."
        ),
    )

    request_uri_parameter_supported: bool | None = pydantic.Field(
        default=False,
        title="Supports `request_uri` parameter?",
        description=(
            "Boolean value specifying whether the OP supports use of the "
            "`request_uri` parameter."
        ),
    )

    require_request_uri_registration: bool | None = pydantic.Field(
        default=True,
        title="Requires pre-regiration?",
        description=(
            "Boolean value specifying whether the OP requires any `request_uri` "
            "values used to be pre-registered."
        ),
    )

    require_signed_request_object: bool | None = pydantic.Field(
        default=True,
        title="Requires pre-regiration?",
        description=(
            "Indicates where authorization request needs to be protected as "
            "**Request Object** and provided through either `request` or "
            "`request_uri` parameter."
        ),
    )

    pushed_authorization_request_endpoint: str | None = pydantic.Field(
        default=None,
        title="Pushed Authorization Request (PAR) endpoint",
        description=(
            "URL of the authorization server's pushed authorization request "
            "endpoint."
        ),
    )

    require_pushed_authorization_requests: bool | None = pydantic.Field(
        default=False,
        title="Requires PAR?",
        description=(
            "Indicates whether the authorization server accepts authorization "
            "requests only via PAR."
        ),
    )

    introspection_signing_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported signature algorithms",
        description=(
            "JSON array containing a list of algorithms supported by the "
            "authorization server for introspection response signing."
        ),
    )

    introspection_encryption_alg_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported encryption algorithms",
        description=(
            "JSON array containing a list of algorithms supported by the "
            "authorization server for introspection response content key "
            "encryption (`alg` value)."
        ),
    )

    introspection_encryption_enc_values_supported: list[str] | None = pydantic.Field(
        default=[],
        title="Supported content encryption algorithms",
        description=(
            "JSON array containing a list of algorithms supported by the "
            "authorization server for introspection response content "
            "encryption (`enc` value)."
        ),
    )

    authorization_response_iss_parameter_supported: bool | None = pydantic.Field(
        default=False,
        title="Supports `iss` parameter in authorization response?",
        description=(
            "Boolean value indicating whether the authorization server "
            "provides the `iss` parameter in the authorization response."
        ),
    )

    authorization_signing_alg_values_supported: list[str] = pydantic.Field(
        default=[],
        title="JARM signature algorithms",
        description=(
            "A JSON array containing a list of the JWS signing algorithms "
            "(`alg` values) supported by the authorization endpoint to "
            "sign the response."
        )
    )

    authorization_encryption_alg_values_supported: list[str] = pydantic.Field(
        default=[],
        title="JARM key wrapping or key agreement algorithms",
        description=(
            "A JSON array containing a list of the JWS signing algorithms "
            "(`alg` values) supported by the authorization endpoint to "
            "encrypt the response."
        )
    )

    authorization_encryption_enc_values_supported: list[str] = pydantic.Field(
        default=[],
        title="JARM encryption algorithms",
        description=(
            "A JSON array containing a list of the JWE encryption algorithms "
            "(`enc` values) supported by the authorization endpoint to "
            "encrypt the response."
        )
    )

    _discovered: bool = pydantic.PrivateAttr(default=False)

    async def discover(self, http: httpx.AsyncClient):
        await self.on_discovered(http)
        return self

    async def on_discovered(
        self,
        http: httpx.AsyncClient
    ) -> None:
        pass