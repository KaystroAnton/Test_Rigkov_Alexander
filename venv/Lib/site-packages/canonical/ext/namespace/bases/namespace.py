# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import ClassVar
from typing import Generic
from typing import Literal
from typing import Self
from typing import TypeVar

import pydantic

from canonical.ext.api import APIResourceModel


T = TypeVar('T', bound=str)
NamespaceTypeLiteral = Literal[
    'webiam.io/namespace',
    'webiam.io/domain',
    'webiam.io/organization',
    'webiam.io/project',
]


class BaseNamespace(APIResourceModel[T], Generic[T], abstract=True):
    __abstract__: ClassVar[bool] = True
    model_config = {'populate_by_name': True}

    type: NamespaceTypeLiteral = pydantic.Field(
        default=...,
        description=(
            "Used to discriminate between various namespace types."
        )
    )

    def can_change(self, old: Self) -> bool:
        return all([
            old.type == self.type
        ])