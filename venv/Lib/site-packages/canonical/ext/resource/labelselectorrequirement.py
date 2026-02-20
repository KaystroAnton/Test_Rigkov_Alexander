# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal

import pydantic

from .apimodel import APIModel


__all__: list[str] = [
    'LabelSelectorRequirement'
]


class LabelSelectorRequirement(APIModel):
    key: str = pydantic.Field(
        default=...,
        description="The label that the selector applies to."
    )

    operator: Literal['In', 'NotIn', 'Exists', 'DoesNotExist'] = pydantic.Field(
        default=...,
        description=(
            "The key\'s relationship to a set of values. Valid operators "
            "are `In`, `NotIn`, `Exists` and `DoesNotExist`."
        )
    )

    values: list[str] = pydantic.Field(
        default=...,
        description=(
            "An array of string values. If the operator is `In` or `NotIn` "
            ", the values array must be non-empty. If the operator is "
            "`Exists` or `DoesNotExist`, the values array must be empty."
        )
    )