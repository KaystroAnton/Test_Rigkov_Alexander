# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
from typing import cast
from typing import Any
from typing import ClassVar
from typing import Self
from typing import TYPE_CHECKING

import pydantic

from canonical.lib.types import SerializableSet
from .apimodel import APIModel
from .apimodelfield import APIModelField
if TYPE_CHECKING:
    from .resource import Resource


class ResourceMetadata(APIModel):
    """The base class for all metadata types."""
    model_config = {'populate_by_name': True}
    allow_on_create: ClassVar[set[str]]
    InputModel: ClassVar[type[Self]]

    annotations: dict[str, Any] = APIModelField(
        default_factory=dict,
        title="Annotations",
        description=(
            "Annotations is an unstructured key value map stored with "
            "a resource that may be set by external tools to store "
            "and retrieve arbitrary metadata. They are not queryable and "
            "should be preserved when modifying objects."
        ),
        when={'create', 'update', 'store', 'view'}
    )

    labels: dict[str, str | None] = APIModelField(
        default_factory=dict,
        title="Labels",
        description=(
            "Map of string keys and values that can be used to organize and "
            "categorize (scope and select) objects."
        ),
        when={'create', 'update', 'store', 'view'}
    )

    tags: SerializableSet[str] = APIModelField(
        default_factory=set,
        description=(
            "An array of tags that may be used to classify an object "
            "if a label or annotation is not applicable."
        ),
        when={'create', 'update', 'store', 'view'}
    )

    @classmethod
    def is_namespaced(cls) -> bool:
        return False

    @classmethod
    def default(cls):
        return cls()

    @classmethod
    def add_to_model(cls, model: type[Resource[Any]]) -> None:
        model.model_fields['metadata'].default = None
        model.model_fields['metadata'].default_factory = cls.default

    @classmethod
    def build_input_model(cls) -> type[Self]:
        fields = set({*set(ResourceMetadata.model_fields), *set(cls.model_fields)})
        attrs: dict[str, Any] = {}
        annotations: dict[str, type | None] = attrs.setdefault('__annotations__', {})
        for name in fields:
            if name not in cls.allow_on_create:
                continue
            field = attrs[name] = cls.model_fields[name]
            annotations[name] = field.annotation
        return cast(type[Self], type(cls.__name__, (ResourceMetadata,), attrs))

    def attach(self, resource: Resource[Any]):
        self._api_version = resource.api_version
        self._kind = resource.kind

    def get_namespace(self) -> str | None:
        return None

    def in_namespace(self, namespace: str | None) -> bool:
        raise NotImplementedError

    def is_labeled(self, names: list[str]) -> bool:
        return all([
            self.labels.get(name) not in {None, 'null'}
            for name in names
        ])

    def merge(self, metadata: 'ResourceMetadata'):
        """Merge :class:`ObjectMeta` `metadata` into this instance."""
        # Only annotations, labels and tags are merged for now.
        self.annotations = {**self.annotations, **metadata.annotations}
        self.labels = {**self.labels, **metadata.labels}
        self.tags = SerializableSet({*self.tags, *metadata.tags})
        return self

    def update_resource_version(self, obj: Resource[Any]):
        pass

    @staticmethod
    def get_metadata_field():
        return pydantic.Field(
            default=...,
            title='Metadata',
            description=(
                "`ObjectMeta` is metadata that all persisted resources "
                "must have, which includes all objects users must create."
            )
        )