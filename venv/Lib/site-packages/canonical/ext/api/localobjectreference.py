# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .apimodel import APIModel
from .bases import BaseReference
from .fields import ReferencedName


__all__: list[str] = [
    'LocalObjectReference'
]


class LocalObjectReference(APIModel, BaseReference):
    """A `LocalObjectReference` instance contains enough
    information to let you locate the referenced object
    inside the same namespace.
    """
    _namespace: str | None = pydantic.PrivateAttr(default=None)
    name: ReferencedName

    def as_name(self) -> str:
        return self.name

    def attach_to_namespace(self, namespace: str):
        self._namespace = namespace
        return self

    def get_namespace(self) -> str | None:
        if self._namespace is None:
            raise TypeError("LocalObjectReference must be attached to a namespace.")
        return self._namespace

    def in_namespace(self, namespace: str) -> bool:
        return True

    def is_cluster(self) -> bool:
        return False

    def is_namespaced(self) -> bool:
        return True

    def with_namespace(self, namespace: str):
        self._namespace = namespace
        return self