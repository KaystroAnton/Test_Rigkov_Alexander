# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Generic
from typing import Literal
from typing import TypeVar

import pydantic


K = TypeVar('K')


class RoleReference(pydantic.BaseModel, Generic[K]):
    api_group: Literal['iam.webiam.io'] = pydantic.Field(
        default='iam.webiam.io',
        alias='apiGroup',
        description=(
            "Must be `iam.webiam.io` for `User`, `ServiceAccount` and "
            "`Group` references."
        )
    )

    kind: K = pydantic.Field(
        default=...,
        description=(
            "Specifies the type of resource being referenced."
        )
    )

    name: str = pydantic.Field(
        default=...,
        description=(
            "Identifies the resource being referenced. For reference "
            "to a `Role`, this implies that the resource is in the "
            "same namespace."
        )
    )

    def is_global(self) -> bool:
        return self.kind == 'ClusterRole'