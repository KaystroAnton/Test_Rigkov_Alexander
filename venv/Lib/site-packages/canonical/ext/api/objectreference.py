# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
from typing import Any
from typing import TypeVar
from typing import TYPE_CHECKING

import pydantic

from .apimodel import APIModel
from .bases import BaseReference
from .fields import APIVersion
from .fields import Kind
from .fields import Name
from .fields import Namespace
if TYPE_CHECKING:
    from .objectmeta import ObjectMeta

__all__: list[str] = [
    'ObjectReference'
]

T = TypeVar('T')


class ObjectReference(APIModel, BaseReference):
    """An `ObjectReference` instance contains enough information
    to let you inspect or modify the referred object.
    """
    model_config = {'populate_by_name': True}

    api_version: APIVersion = pydantic.Field(
        default=...,
        description=(
            "Specifies the API version of the referent. Cannot be updated."
        ),
        frozen=True
    )

    kind: Kind = pydantic.Field(
        default=...,
        description=(
            "Kind of the referent. Cannot be updated. In `CamelCase`."
        ),
        frozen=True
    )

    name: Name = pydantic.Field(
        default=...,
        description=(
            "The `.metadata.name` of of the referent. Cannot be "
            "updated."
        ),
        frozen=True
    )

    namespace: Namespace = pydantic.Field(
        default='',
        description="The namespace of the referent.",
        frozen=False
    )

    resource_version: str = pydantic.Field(
        default='',
        description="Specific resourceVersion to which this reference is made, if any."
    )

    uid: int | None = pydantic.Field(
        default=None,
        description="UID of the referent."
    )

    @property
    def api_group(self):
        return self.api_version.group

    def as_name(self) -> str:
        return self.name

    def attach(self, metadata: ObjectMeta[Any]):
        self.resource_version = getattr(metadata, 'resource_version', '')
        self.uid = getattr(metadata, 'uid', None)
        self.namespace = getattr(metadata, 'namespace', '')
        return self

    def cache_key(self, prefix: str):
        if self.namespace:
            prefix = f'{prefix}:{self.namespace}'
        return f'{prefix}:{self.name}'

    def get_namespace(self) -> str | None:
        return self.namespace or None

    def is_cluster(self) -> bool:
        return not bool(self.namespace)

    def in_namespace(self, namespace: str) -> bool:
        return self.namespace == namespace

    def is_local(self) -> bool:
        return not self.is_cluster()

    def is_namespaced(self) -> bool:
        return bool(self.namespace)

    def with_namespace(self, namespace: str):
        if namespace != self.namespace:
            raise ValueError(
                f"{type(self).__name__}.namespace '{self.namespace}' is not "
                f"equal to '{namespace}'."
            )
        return self