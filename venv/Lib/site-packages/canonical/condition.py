# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
from typing import Generic
from typing import TypeVar

import pydantic


R = TypeVar('R')
S = TypeVar('S')


class Condition(pydantic.BaseModel, Generic[S]):
    """Describes the condition of a :class:`VersionedResource`."""

    timestamp: datetime.datetime = pydantic.Field(
        default=...,
        description=(
            "Specifies the date and time at which the condition "
            "emerged."
        )
    )

    message: str = pydantic.Field(
        default='',
        description=(
            "A human readable message indicating details about "
            "the transition. This may be an empty string."
        )
    )

    observed_generation: int = pydantic.Field(
        default=...,
        alias='observedGeneration',
        description=(
            "Represents the `.metadata.generation` that the "
            "condition was set based upon. For instance, if "
            "`.metadata.generation` is currently 12, but "
            "the `.status.conditions[x].observedGeneration` "
            "is 9, the condition is out of date with respect "
            "to the current state of the instance."
        )
    )

    status: S = pydantic.Field(
        default=...,
        description=(
            "Contains a programmatic identifier indicating the "
            "status of the condition's last transition. "
            "Producers of specific condition types may define "
            "expected values and meanings for this field, "
            "and whether the values are considered a guaranteed "
            "API. This field may not be empty."
        )
    )

    def is_final(self) -> bool:
        return False