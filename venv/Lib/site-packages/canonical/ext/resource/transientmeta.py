# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
import datetime
from typing import Any
from typing import TYPE_CHECKING

import pydantic

if TYPE_CHECKING:
    from .resource import Resource
from .resourcekey import ResourceKey
from .resourcemetadata import ResourceMetadata


class TransientMeta(ResourceMetadata):
    model_config = {'populate_by_name': True}
    
    created: datetime.datetime | None = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        title="Created",
        description=(
            "The `created` field represents the date and time at which this "
            "object was created."
        ),
        frozen=True
    )

    @classmethod
    def is_namespaced(cls) -> bool:
        return False

    @classmethod
    def default(cls):
        return cls()

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def key(self) -> ResourceKey[Any]:
        raise NotImplementedError

    @property
    def resource_version(self) -> None:
        return None

    @classmethod
    def add_to_model(cls, model: type[Resource[Any]]) -> None:
        model.model_fields['metadata'].default = None
        model.model_fields['metadata'].default_factory = cls.default

    @classmethod
    def build_input_model(cls):
        return cls

    def attach(self, resource: Resource[Any]):
        self._api_version = resource.api_version
        self._kind = resource.kind

    def get_namespace(self) -> str | None:
        return None

    def update_resource_version(self, obj: Resource[Any]):
        pass

    @staticmethod
    def get_metadata_field():
        return pydantic.Field(
            default=None,
            title='Metadata',
            description=(
                "`ObjectMeta` is metadata that all persisted resources "
                "must have, which includes all objects users must create."
            )
        )