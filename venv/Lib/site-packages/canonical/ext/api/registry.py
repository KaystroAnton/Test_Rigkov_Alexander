# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import APIResourceType
    from .meta import APIVersionedMeta


__all__: list[str] = [
    'get_meta',
    'register',
]


class ResourceRegistry:
    models: dict[str, APIVersionedMeta[APIResourceType]]

    def __init__(self) -> None:
        self.models = {}

    def register(self, meta: APIVersionedMeta[APIResourceType]) -> None:
        if meta.plural:
            self.models[meta.plural] = meta
        if meta.kind:
            self.models[meta.kind] = meta

    def get_meta(
        self,
        api_group: str, *,
        kind: str | None = None,
        plural: str | None = None
    ) -> APIVersionedMeta[APIResourceType]:
        if not bool(kind) ^ bool(plural):
            raise TypeError(
                "Specify either the 'kind' or 'plural' parameter, "
                "but not both."
            )
        return self.models[str(kind or plural)]


_registry: ResourceRegistry = ResourceRegistry()
get_meta = _registry.get_meta
register = _registry.register