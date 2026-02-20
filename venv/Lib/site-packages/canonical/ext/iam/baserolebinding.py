# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Generic
from typing import TypeVar

import pydantic

from canonical.ext.api import APIResourceModel
from .rolereference import RoleReference
from .subject import Subject


RefType = TypeVar('RefType')


class BaseRoleBinding(APIResourceModel[str], Generic[RefType], abstract=True):
    subjects: list[Subject] = pydantic.Field(
        default=...,
        description=(
            "Holds references to the objects the role applies to."
        ),
        min_length=1
    )

    role_ref: RoleReference[RefType] = pydantic.Field(
        default=...,
        alias='roleRef',
        description=(
            "The `roleRef` property must reference a `Role` in the current namespace "
            "or a `GlobalRole` in the global namespace. If `roleRef` cannot be resolved, "
            "the Authorizer must return an error."
        )
    )

    def is_global(self) -> bool:
        return self.role_ref.is_global()