# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Iterable
from typing import Protocol

from canonical.protocols import IDeferrable
from ..types import PermissionSet


class IResourceAuthorizationContext(IDeferrable, Protocol):

    def has_permissions(self, permissions: Iterable[str]) -> set[str]: ...
    def is_authenticated(self) -> bool: ...
    def is_authorized(self) -> bool: ...
    async def has(self, permissions: str | set[str]) -> bool: ...
    async def get_permissions(self, permissions: set[str]) -> PermissionSet: ...