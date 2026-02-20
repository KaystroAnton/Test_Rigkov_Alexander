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

from .apidescriptor import APIDescriptor


class ResourceServerList(pydantic.BaseModel):
    kind: Literal['ResourceServerList'] = pydantic.Field(
        default='ResourceServerList'
    )

    servers: list[APIDescriptor] = pydantic.Field(
        default_factory=list
    )

    index: dict[str, APIDescriptor] = pydantic.Field(
        default_factory=dict,
        exclude=True
    )

    def model_post_init(self, _: Any) -> None:
        self.index = {s.host: s for s in self.servers}

    def add(self, server: APIDescriptor) -> None:
        if not self.index.get(server.host):
            self.index[server.host] = server
            self.servers.append(server)