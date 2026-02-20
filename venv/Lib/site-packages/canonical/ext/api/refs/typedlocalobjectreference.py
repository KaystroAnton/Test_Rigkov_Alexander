# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Self

import pydantic

from ..apiversioned import APIModel
from ..bases.reference import BaseReference
from ..builders import APIModelClassBuilder
from ..fields import Kind


__all__: list[str] = [
    'TypedLocalObjectReference'
]


class TypedLocalObjectReference(APIModel, BaseReference):
    """A `TypedLocalObjectReference` instance contains enough
    information to let you locate the typed referenced object
    inside the same namespace.
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

    @classmethod
    def build_class(
        cls,
        builder: APIModelClassBuilder[Self],
        **kwargs: Any
    ):
        super().build_class(builder, **kwargs)
        builder.set_field_literal('api_group', kwargs.get('api_group'))
        builder.set_field_literal('kind', kwargs.get('kind'))