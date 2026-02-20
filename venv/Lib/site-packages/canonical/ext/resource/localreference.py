# Copyright (C) 2023-2024 Cochise Ruhulessin
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

from .objectreferencemodel import ObjectReferenceModel


__all__: list[str] = [
    'LocalReference'
]

T = TypeVar('T')


class LocalReference(ObjectReferenceModel[T], Generic[T]):
    """A reference to a local object (in the same namespace)."""
    _namespace: str | None = pydantic.PrivateAttr(default=None)

    def is_local(self) -> bool:
        return True

    def get_namespace(self) -> str | None:
        assert self._namespace is not None
        return self._namespace

    def is_namespaced(self) -> bool:
        return True

    def with_namespace(self, namespace: str):
        self._namespace = namespace
        return self