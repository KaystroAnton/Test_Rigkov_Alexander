# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from .localobjectreference import LocalObjectReference


__all__: list[str] = [
    'ClusterObjectReference'
]


class ClusterObjectReference(LocalObjectReference):
    """A `ClusterlObjectReference` instance contains enough
    information to let you locate the referenced object
    inside the same cluster.
    """

    @property
    def model(self) -> type[Any]:
        assert self._reference_model is not None
        return self._reference_model

    def as_name(self) -> str:
        return self.name

    def attach_to_namespace(self, namespace: str) -> None:
        raise NotImplementedError

    def get_namespace(self) -> str | None:
        return None

    def in_namespace(self, namespace: str) -> bool:
        return False

    def is_cluster(self) -> bool:
        return True

    def is_namespaced(self) -> bool:
        return True