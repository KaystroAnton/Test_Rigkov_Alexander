# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .apiversioned import APIVersioned
from .bases import BaseReference
from .fields import APIVersion
from .fields import Kind
from .fields import UID


__all__: list[str] = [
    'OwnerReference'
]


class OwnerReference(APIVersioned, BaseReference, group='', version='v1'):
    """An `OwnerReference` instance contains enough information to let you
    identify an owning object. An owning object must be in the same namespace
    as the dependent, or be cluster-scoped, so there is no namespace field.
    """

    api_version: APIVersion = pydantic.Field(
        default=...,
        description="API version of the referent."
    )

    block_owner_deletion: bool = pydantic.Field(
        default=True,
        alias='blockOwnerDeletion',
        description=(
            "If true, AND if the owner has the `foregroundDeletion` finalizer, "
            "then the owner cannot be deleted from the key-value store until "
            "this reference is removed."
        )
    )

    controller: bool = pydantic.Field(
        default=False,
        description=(
            "If true, this reference points to the managing controller."
        )
    )

    kind: Kind = pydantic.Field(
        default=...,
        description="Kind of the referent."
    )

    name: str = pydantic.Field(
        default=...,
        description="Name of the referent."
    )

    uid: UID = pydantic.Field(
        default=...,
        description="UID of the referent"
    )

    def as_name(self) -> int | str:
        return self.name

    def attach_to_namespace(self, namespace: str | None) -> None:
        if namespace:
            raise NotImplementedError

    def is_namespaced(self) -> bool:
        raise NotImplementedError

    def get_namespace(self) -> str | None:
        return None