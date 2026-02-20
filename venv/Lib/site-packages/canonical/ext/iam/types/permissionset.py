# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .permission import Permission
from .permissionwildcard import PermissionWildcard


PermissionType = Permission | PermissionWildcard


class PermissionSet(set[PermissionType]):

    def has(self, permission: str) -> bool:
        for granted in self:
            is_granted = granted.matches(permission)
            if is_granted:
                break
        else:
            is_granted = False
        return is_granted