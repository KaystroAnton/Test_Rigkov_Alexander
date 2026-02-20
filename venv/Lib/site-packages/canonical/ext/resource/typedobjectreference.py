# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal

import pydantic

from .apiversioned import APIModel
from .basereference import BaseReference
from .fields import Kind
from .fields import Namespace


__all__: list[str] = [
    'TypedObjectReference'
]


class TypedObjectReference(APIModel, BaseReference):
    """A `TypedObjectReference` instance contains enough information to let
    you inspect or modify the referred object of the given type.
    """
    api_group: str = pydantic.Field(
        default=...,
        alias='apiGroup',
        description=(
            "The `apiGroup` field is the group for the resource being "
            "referenced. If `apiGroup` is not specified, the specified "
            "`kind` must be in the core API group. For any other "
            "third-party types, `apiGroup` is required."
        )
    )

    kind: Kind = pydantic.Field(
        default=...,
        description="The type of resource being referenced."
    )

    name: str = pydantic.Field(
        default=...,
        description="The name of resource being referenced."
    )

    namespace: Namespace = pydantic.Field(
        default='',
        description=(
            "The namespace of resource being referenced, or an "
            "empty string for cluster resources."
        )
    )

    def __init_subclass__(cls, **kwargs: Any):
        return super().__init_subclass__()

    @classmethod
    def __pydantic_init_subclass__(
        cls,
        *,
        namespaced: bool | None = None,
        api_group: str | None = None,
        kind: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        fields = cls.model_fields
        if api_group is not None:
            fields['api_group'].annotation = Literal[f'{api_group}']
        if kind is not None:
            fields['kind'].annotation = Literal[f'{kind}']
        if not namespaced:
            cls.model_fields['namespace'].annotation = Literal['']
            del cls.model_fields['namespace']
        assert cls.model_rebuild(force=True)

    def attach_to_namespace(self, namespace: str) -> None:
        pass