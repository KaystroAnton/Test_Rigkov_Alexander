# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi
import logging

from canonical.ext.iam import BaseAuthorizationContext
from canonical.ext.iam.types import PermissionSet
from canonical.ext.resource import ResourceType
from canonical.lib.protocols import ICache
from ..resourceclient import ResourceClient
from .annotations import AccessPolicyServerURL
from .annotations import DefaultInspector
from .impersonationauth import ImpersonationAuth
from .requestemail import RequestEmail
from .resourcerepository import ResourceRepository


__all__: list[str] = [
    'RemoteAuthorizationContext'
]


class RemoteAuthorizationContext(BaseAuthorizationContext):
    model: type[ResourceType]
    logger: logging.Logger = logging.getLogger('uvicorn')
    verb: str

    @property
    def client(self) -> ResourceClient:
        return ResourceClient(
            auth=self.auth,
            base_url=self.server_url,
            cache=self.cache,
        )

    @property
    def cache(self) -> ICache:
        return getattr(self.request.state, 'cache')

    def __init__(
        self,
        request: fastapi.Request,
        auth: ImpersonationAuth,
        resources: ResourceRepository,
        inspector: DefaultInspector,
        server_url: AccessPolicyServerURL,
        email: RequestEmail,
    ):
        super().__init__()
        self.auth = auth
        self.email = email
        self.granted = PermissionSet()
        self.inspector = inspector
        self.repo = resources
        self.request = request
        self.server_url = server_url
        self.subject_type = 'User'

    async def setup(self):
        self.logger.info("Initializing authorization context (subject: %s)", self.email)
        self.model: type[ResourceType] = getattr(self.request.state, 'model')
        self.meta = self.inspector.inspect(self.model)
        self.namespace: str | None = getattr(self.request.state, 'namespace', None)
        self.verb: str = getattr(self.request.state, 'verb')
        self.api_group = self.meta.api_group
        self.plural = self.meta.plural

        assert self.plural
        self.permission = self.get_permission_name(
            api_group=self.api_group,
            plural=self.plural,
            verb=self.verb
        )

        async with self.client as client:
            self.logger.info(
                "Inspecting permissions (server: %s, subject: %s, permission: %s)",
                client.base_url,
                self.email,
                self.permission
            )
            self.granted = PermissionSet(
                await client.permissions(
                    namespace=self.namespace,
                    permission=self.permission,
                    cache_key=self.email or 'allUsers'
                )
            )

    def is_authenticated(self) -> bool:
        return self.email is not None

    def is_authorized(self) -> bool:
        return self.granted.has(self.permission)