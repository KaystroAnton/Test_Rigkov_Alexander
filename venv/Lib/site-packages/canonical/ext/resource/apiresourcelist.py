# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any, Literal

import pydantic

from .resourcemeta import ResourceMeta


class APIResource(pydantic.BaseModel):
    name: str
    namespaced: bool
    kind: str
    verbs: list[str] = []

    def add(self, verb: str) -> None:
        self.verbs = list(sorted({verb, *self.verbs}))

    def path(
        self,
        api_version: str,
        name: str | int | None = None,
        namespace: str | None = None
    ) -> str:
        url = api_version
        if self.namespaced:
            if namespace is None:
                raise TypeError(
                    "The `namespace` parameter can not be None."
                )
            url = f'{url}/namespaces/{namespace}'
        url = f'{url}/{self.name}'
        if name is not None:
            url = f'{url}/{name}'
        return url


class APIResourceList(pydantic.BaseModel):
    kind: Literal['APIResourceList'] = 'APIResourceList'
    groupVersion: str
    resources: list[APIResource] = []
    _index: dict[str, APIResource] = pydantic.PrivateAttr(default_factory=dict)

    def model_post_init(self, _: Any) -> None:
        self._index = {
            resource.kind: resource
            for resource in self.resources
        }

    def add(self, meta: ResourceMeta, plural: str | None = None) -> APIResource:
        plural = plural or meta.plural
        resource = self._index.get(meta.kind)
        if resource is None:
            resource = APIResource(
                name=plural,
                namespaced=meta.namespaced,
                kind=meta.kind,
            )
            self._index[meta.kind] = resource
            self.resources = list(sorted([resource, *self.resources], key=lambda x: x.kind))
        return resource

    def get(self, kind: str) -> APIResource:
        if kind not in self._index:
            raise LookupError(
                f"Unknown resource: {kind}. Supported resources for this group "
                f"are: {str.join(', ', sorted(self._index.keys()))}"
            )
        return self._index[kind]

    def path(self, group: str) -> str:
        return f'{group}/{self.groupVersion}' if group else self.groupVersion