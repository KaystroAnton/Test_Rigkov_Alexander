# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Generic
from typing import TypeVar

import pydantic

from .objectmeta import ObjectMeta
from .objectmeta import N


T = TypeVar('T')


class NamespacedObjectMeta(ObjectMeta[N], Generic[N]):
    allow_on_create = {'name', 'namespace'}

    namespace: str = pydantic.Field(
        default=...,
        title="Namespace",
        description=(
            "Namespace defines the space within which each name must "
            "be unique. An empty namespace is equivalent to the `default` "
            "namespace, but `default` is the canonical representation. "
            "Not all objects are required to be scoped to a namespace - "
            "the value of this field for those objects will be empty. "
            "Must be a DNS_LABEL. Cannot be updated."
        )
    )

    @classmethod
    def is_namespaced(cls) -> bool:
        return True

    def get_namespace(self) -> str | None:
        return self.namespace

    def in_namespace(self, namespace: str | None) -> bool:
        return namespace == self.namespace