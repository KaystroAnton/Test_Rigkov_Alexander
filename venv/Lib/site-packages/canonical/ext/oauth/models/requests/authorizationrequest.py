# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import secrets
from typing import Any


from canonical.ext.fastapi.mixins import QueryModelMixin
from canonical.ext.oauth.protocols import IRegisteredClient
from canonical.ext.oauth.types import ResponseTypeLiteral
from canonical.ext.oauth.types import RedirectURI
from canonical.ext.oauth.types import URLSafeClientID
from canonical.lib import FormDataModel
from canonical.lib.types import HTTPResourceLocator


class AuthorizationRequest(FormDataModel, QueryModelMixin):
    model_config = {'extra': 'forbid'}
    client_id: URLSafeClientID | str
    response_type: ResponseTypeLiteral
    redirect_uri: RedirectURI | None = None
    state: str | None = None

    @classmethod
    def new(cls, **kwargs: Any):
        kwargs.setdefault('state', secrets.token_hex(32))
        return cls.model_validate(kwargs)

    def authorize(self, authorization_endpoint: HTTPResourceLocator) -> HTTPResourceLocator:
        return authorization_endpoint.with_query(**self.model_dump(mode='json', exclude_none=True))

    def proxy(self, endpoint: str, client_id: str, redirect_uri: str, state: str) -> str:
        """Proxies the authorization request. Return a string containing the
        full authorization URL, with the `client_id`,  `redirect_uri` and
        `state` parameters replaced by the given values.
        """
        clone = self.model_validate({
            **self.model_dump(mode='json'),
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'state': state
        })
        return str(clone.with_endpoint('GET', endpoint))

    def validate_client(self, client: IRegisteredClient):
        if not client.allows_redirect(self.redirect_uri):
            raise NotImplementedError(f"Redirection to {self.redirect_uri} is not allowed.")
        if not client.allows_response_type(self.response_type):
            raise NotImplementedError(
                "The client does not allow the requested response type."
            )

    def __str__(self):
        return f'{self._url}?{self.model_dump_urlencoded()}'