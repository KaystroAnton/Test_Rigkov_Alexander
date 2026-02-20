# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal

import pydantic

from .apigroupversionlist import APIGroupVersionList


class APIDescriptor(pydantic.BaseModel):
    host: str = pydantic.Field(
        default=...
    )

    kind: Literal['APIDescriptor'] = pydantic.Field(
        default='APIDescriptor'
    )

    groups: list[APIGroupVersionList] = pydantic.Field(
        default_factory=list
    )

    index: dict[str, APIGroupVersionList] = pydantic.Field(
        default_factory=dict,
        exclude=True
    )

    def model_post_init(self, _: Any) -> None:
        self.index = {g.group: g for g in self.groups}

    def add(self, group: APIGroupVersionList) -> None:
        if not self.index.get(group.group):
            self.index[group.group] = group
            self.groups.append(group)