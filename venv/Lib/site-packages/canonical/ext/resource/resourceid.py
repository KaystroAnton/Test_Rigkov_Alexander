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


__all__: list[str] = [
    'ResourceID'
]

N = TypeVar('N')
T = TypeVar('T')


class ResourceID(pydantic.BaseModel, Generic[N, T]):
    """A container to reference an `id` for any resource type. A resource "
    is a generic term for something you (a developer) may want to interact "
    "with through one of our API's.
    """
    type: N = pydantic.Field(
        default=...,
        description="The resource type this `ResourceID` is for."
    )

    name: T = pydantic.Field(
        default=...,
        description=(
            "The type-specific id. This should correspond to "
            "the id used in the type-specific API's."
        )
    )