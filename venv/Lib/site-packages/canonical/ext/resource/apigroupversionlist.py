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

from .apiresourcelist import APIResourceList


class APIGroupVersionList(pydantic.BaseModel):
    group: str = pydantic.Field(
        default=...
    )

    kind: Literal['APIGroupVersionList'] = pydantic.Field(
        default='APIGroupVersionList'
    )

    versions: list[APIResourceList] = pydantic.Field(
        default_factory=list
    )

    index: dict[str, APIResourceList] = pydantic.Field(
        default_factory=dict,
        exclude=True
    )

    def model_post_init(self, _: Any) -> None:
        self.index = {v.groupVersion: v for v in self.versions}

    def add(self, version: APIResourceList) -> None:
        if not self.index.get(version.groupVersion):
            self.index[version.groupVersion] = version
            self.versions.append(version)