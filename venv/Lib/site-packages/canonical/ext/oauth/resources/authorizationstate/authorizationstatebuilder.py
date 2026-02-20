# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import secrets
from typing import Any

import fastapi

from canonical.ext.api.bases import BaseResourceBuilder
from canonical.ext.fastapi.params import ResourceRepository
from canonical.ext.oauth.models import AuthorizationRequest
from canonical.ext.oauth.models import ServerMetadata
from canonical.ext.oauth.protocols import IRegisteredClient
from canonical.lib.types import HTTPResourceLocator
from .authorizationstate import AuthorizationState


class AuthorizationStateBuilder(BaseResourceBuilder[AuthorizationState]):
    client: IRegisteredClient | None = None
    mode: str
    model = AuthorizationState

    def __init__(self, request: fastapi.Request, repo: ResourceRepository):
        super().__init__(repo)
        self.request = request
        self.mode = 'proxy'

    def get_model_input(self) -> dict[str, Any]:
        return {
            **super().get_model_input(),
            'status': {
                'changed': self.now,
                'version': 1,
                'message': '',
                'current': 'Created'
            }
        }

    def forward(self, forward_to: str):
        self.mode = self.spec['redirect_mode'] = 'forwarding'
        self.spec['forward_url'] = forward_to

    def proxy(self, callback_uri: str):
        self.mode = self.spec['redirect_mode'] = 'proxy'
        self.spec['proxy_redirection_endpoint'] = callback_uri

    def with_authorization_endpoint(self, url: str):
        self.spec['authorization_endpoint'] = url

    def with_callback(self, redirect_uri: str):
        self.spec['redirect_uri'] = redirect_uri

    def with_client(self, client: IRegisteredClient):
        self.spec['client_id'] = client.id

    def with_client_id(self, client_id: str):
        self.spec['client_id'] = client_id

    def with_issuer(self, issuer: str):
        self.spec['issuer'] = issuer

    def with_metadata(self, metadata: ServerMetadata):
        self.with_issuer(metadata.issuer)
        if metadata.authorization_endpoint:
            self.with_authorization_endpoint(metadata.authorization_endpoint)
        if metadata.token_endpoint:
            self.with_token_endpoint(metadata.token_endpoint)

    def with_params(
        self,
        params: AuthorizationRequest | HTTPResourceLocator,
    ):
        if isinstance(params, HTTPResourceLocator):
            params = AuthorizationRequest.model_validate(params.query)
            self.with_client_id(str(params.client_id))
            if params.state:
                self.metadata['name'] = params.state
        self.spec['params'] = params

    def with_redirect_uri(self, uri: str):
        self.spec['redirect_uri'] = uri

    def with_token_endpoint(self, url: str):
        self.spec['token_endpoint'] = url

    async def prepare(self):
        if not self.metadata.get('name'):
            self.metadata['name'] = secrets.token_hex(32)