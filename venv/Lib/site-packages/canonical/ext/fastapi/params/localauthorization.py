# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging
from typing import Iterable

import fastapi

from canonical.ext.api import APIResourceType
from canonical.ext.iam import BaseAuthorizationContext
from canonical.ext.iam import ClusterRole
from canonical.ext.iam import ClusterRoleBinding
from canonical.ext.iam import Role
from canonical.ext.iam import RoleBinding
from canonical.ext.iam.types import Permission
from canonical.ext.iam.types import PermissionSet
from canonical.ext.namespace import Namespace
from canonical.lib.protocols import ICache
from .annotations import DefaultInspector
from .resourcerepository import ResourceRepository


class LocalAuthorizationContext(BaseAuthorizationContext):
    cache_ttl: int = 900
    logger: logging.Logger = logging.getLogger('uvicorn')
    roles: set[str]
    _cluster_roles: dict[str, ClusterRole] = NotImplemented
    _ready: bool = False

    @property
    def cache(self) -> ICache:
        return getattr(self.request.state, 'cache')

    @property
    def email(self) -> str | None:
        return getattr(self.request.state, 'email', None)

    def __init__(
        self,
        inspector: DefaultInspector,
        repo: ResourceRepository,
        request: fastapi.Request,
    ):
        super().__init__()
        self.inspector = inspector
        self._cluster_permissions = LocalAuthorizationContext._cluster_roles
        self.granted = PermissionSet()
        self.repo = repo
        self.request = request
        self.subject_type = 'User'

    async def get_cluster_bindings(self):
        cache_key = f'clusterrolebindings:users:{self.email or "allUsers"}'
        bindings: list[ClusterRoleBinding] | None = await self.cache.get(
            key=cache_key,
            decoder=list[ClusterRoleBinding]
        )
        if bindings is None:
            bindings = []
            public = self.repo.query(
                model=ClusterRoleBinding,
                filters=[
                    ('subjects.kind', '=', self.subject_type),
                    ('subjects.name', '=', 'allUsers'),
                ]
            )
            if self.email is not None:
                self.logger.debug(
                    "Retrieving global role bindings (kind: %s, email: %s)",
                    self.subject_type,
                    self.email
                )
                user = self.repo.query(
                    model=ClusterRoleBinding,
                    filters=[
                        ('subjects.kind', '=', self.subject_type),
                        ('subjects.name', '=', self.email),
                    ]
                )
                bindings = [*await user]
            bindings = [*bindings, *await public]
            await self.cache.set(
                key=cache_key,
                value=bindings,
                encoder=list[ClusterRoleBinding],
                ttl=self.cache_ttl
            )
        return bindings

    def get_namespace_roles(self, roles: Iterable[str]):
        assert self.namespace is not None
        return self.repo.query(
            model=Role,
            # TODO: Current implementation causes the query
            # to return not any object if there are multiple
            # roles.
            #filters=[('metadata.name', '=', list(roles))],
            namespace=self.namespace
        )

    def is_authenticated(self) -> bool:
        return self.email is not None

    def is_authorized(self) -> bool:
        return self.is_granted(self.permission)

    def is_granted(self, permission: str) -> bool:
        return self.granted.has(permission)

    async def get_permissions(self, permissions: set[str]) -> PermissionSet:
        return PermissionSet({Permission(p) for p in permissions if self.is_granted(p)})

    async def get_namespace_permissions(self, roles: Iterable[str]) -> PermissionSet:
        permissions = PermissionSet()
        async for role in self.get_namespace_roles(roles):
            if role.metadata.name not in roles:
                continue
            permissions.update(role.permissions)
        return permissions

    async def has(self, permissions: str | set[str]) -> bool:
        if isinstance(permissions, str):
            permissions = {permissions}
        granted = await self.get_permissions(permissions)
        return set(granted) == permissions

    async def get_namespace_bindings(self):
        cache_key = f'rolebindings:users:{self.email}'
        bindings = await self.cache.get(cache_key, list[RoleBinding])
        if bindings is None:
            self.logger.debug(
                "Retrieving local role bindings (namespace: %s, kind: %s, email: %s)",
                self.namespace,
                self.subject_type,
                self.email
            )
            q = self.repo.query(
                model=RoleBinding,
                filters=[
                    ('subjects.kind', '=', self.subject_type),
                    ('subjects.name', '=', str(self.email)),
                ],
                namespace=self.namespace
            )
            bindings = [x async for x in q]
            await self.cache.set(cache_key, bindings, list[RoleBinding], ttl=self.cache_ttl)
        return bindings

    async def setup(self):
        self.model: type[APIResourceType] = getattr(self.request.state, 'model')
        self.meta = self.inspector.inspect(self.model)

        assert self.meta.plural
        self.namespace: str | None = getattr(self.request.state, 'namespace', None)
        self.verb: str = getattr(self.request.state, 'verb')
        self.api_group = self.meta.api_group
        self.plural = self.meta.plural
        self.permission = self.get_permission_name(self.api_group, self.plural, self.verb)
        self.logger.debug(
            "Endpoint permission is %s (endpoint: %s).",
            self.permission,
            self.request.url.path
        )

        # Namespace is a special cause because permissions in the namespace
        # also apply to the namespace itself.
        if self.namespace is None and self.model == Namespace:
            # This will be none for cluster resources.
            self.namespace = getattr(self.request.state, 'name', None)
    
        await self.setup_cluster()

        scoped_roles: set[str] = set()
        global_roles: set[str] = set()
        try:
            for binding in await self.get_cluster_bindings():
                role = self._cluster_roles[binding.role_ref.name]
                self.granted.update(role.permissions)
        except KeyError:
            # Occurs when cluster roles have been added and made the
            # cache stale.
            return
        if self.namespace is not None:
            for obj in await self.get_namespace_bindings():
                if obj.is_global():
                    global_roles.add(obj.role_ref.name)
                else:
                    scoped_roles.add(obj.role_ref.name)

            self.granted |= await self.get_namespace_permissions(scoped_roles)
        self.logger.debug(
            "Granted permissions are %s (endpoint: %s, subject: %s)",
            ', '.join(sorted(map(str, self.granted))),
            self.request.url,
            self.email
        )

    async def get_cluster_roles(self) -> list[ClusterRole]:
        meta = self.inspector.inspect(ClusterRole)
        cache_key = meta.cache_prefix
        roles = await self.cache.get(cache_key, list[ClusterRole])
        if roles is None:
            self.logger.debug("Retrieving cluster roles and permissions")
            roles = [x async for x in self.repo.all(ClusterRole)]
            await self.cache.set(cache_key, roles, list[ClusterRole], ttl=3600)
        return roles

    async def setup_cluster(self):
        if self._cluster_roles != NotImplemented:
            return
        self._cluster_roles = {
            x.metadata.name: x
            for x in await self.get_cluster_roles()
        }