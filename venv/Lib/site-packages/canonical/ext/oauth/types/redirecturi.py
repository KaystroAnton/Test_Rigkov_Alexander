# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import ipaddress
import urllib.parse
from typing import Any
from typing import Literal
from typing import TypeVar
from typing import Union

from canonical import Hostname
from pydantic_core import CoreSchema
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from pydantic import GetCoreSchemaHandler
from pydantic import GetJsonSchemaHandler


T = TypeVar('T', bound='RedirectURI')


OOB_URLS: set[str] = {
    "urn:ietf:wg:oauth:2.0:oob",
    "urn:ietf:wg:oauth:2.0:oob:auto"
}

IPV6_LOOPBACK_LITERALS: set[str] = {'::1', '0:0:0:0:0:0:0:1'}


class RedirectURI(str):
    __module__: str = 'headless.ext.oidc.types'
    domain: Hostname | None = None
    url: urllib.parse.ParseResult

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema['title'] = 'Redirect URI'
        json_schema['description'] = (
            "The redirect URI specifies where the authorization server "
            "must redirect the user-agent after an authorization request. "
        )
        return json_schema

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

    def __new__(cls, v: str):
        instance = super().__new__(cls, v)
        instance.url = p = urllib.parse.urlparse(v)
        if not v:
            raise ValueError("The redirect_uri parameter can not be empty.")
        if len(v) > 2048:
            raise ValueError('The redirect_uri parameter is too long to be a valid URL.')
        if v in OOB_URLS:
            raise ValueError('OOB is a security risk.')
        if not p.scheme or not p.netloc:
            raise ValueError('The redirect_uri parameter did not specify a valid URL.')
        if p.query:
            raise ValueError('Query parameters must not be used in the redirect URI.')
        if p.fragment:
            raise ValueError('URL fragment must not be used in the redirect URI.')

        # Check if the value is a valid hostname or an IP address.
        if p.hostname is None:
            raise ValueError("Invalid redirect URI.")
        if p.hostname == 'localhost':
            # Clients should use loopback IP literals rather than the
            # string localhost as described in Section 8.4.2.
            # (OAuth 2.1 draft).
            raise ValueError('local redirect URIs must use loopback IP literals.')
        try:
            instance.domain = Hostname.validate(p.hostname) # type: ignore
            if p.scheme != 'https':
                raise ValueError('the https scheme must be used.')
        except ValueError:
            try:
                ip = ipaddress.ip_address(p.hostname)
                p.port
            except ValueError:
                raise ValueError(f'Redirect URI must hold a valid hostname or IP address: {p.hostname}.')
            else:
                if isinstance(ip, ipaddress.IPv6Address)\
                and not str.startswith(p.netloc, '['):
                    raise ValueError("Invalid redirect URI.")
                if not ip.is_loopback and p.scheme != 'https':
                    raise ValueError('the https scheme must be used.')

        return instance
    
    def can_redirect(self, redirect_uri: Union[str, 'RedirectURI']) -> bool:
        """Return a boolean indicating redirection to `redirect_uri`
        is allowed by this instance.
        """
        # Authorization servers MUST require clients to register their
        # complete redirect URI (including the path component).
        # Authorization servers MUST reject authorization requests
        # that specify a redirect URI that doesn't exactly match
        # one that was registered, with an exception for loopback
        # redirects, where an exact match is required except for
        # the port URI component
        if not isinstance(redirect_uri, RedirectURI):
            redirect_uri = RedirectURI(redirect_uri)
        return all([
            self.url.scheme == redirect_uri.url.scheme,
            (self.url.netloc == redirect_uri.url.netloc)\
                or (self.is_loopback() and redirect_uri.is_loopback()),
            self.url.path == redirect_uri.url.path
        ])

    def redirect(
        self,
        allow_params: bool = False,
        mode: Literal['query', 'fragment'] = 'query',
        **params: Any
    ) -> str:
        """Create a redirect URI with the given params."""
        params = {k: v for k, v in params.items() if v is not None}
        p: list[str] = list(urllib.parse.urlparse(self)) # type: ignore
        p[4] = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        return urllib.parse.urlunparse(p)

    def is_loopback(self) -> bool:
        """Return a boolean indicating if the :class:`RedirectURI` point
        to a local loopback address.
        """
        assert self.url.hostname is not None
        try:
            ip = ipaddress.ip_address(self.url.hostname)
            return ip.is_loopback
        except ValueError:
            return False

    def __repr__(self) -> str: # pragma: no cover
        return f'RedirectURI({self})'