# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
import enum
from typing import cast
from typing import Any
from typing import Generic
from typing import TypeVar

import pydantic

from .condition import Condition


C = TypeVar('C', bound=Condition[Any])



class CurrentResourceState(pydantic.BaseModel):
    """Describes the current state of a :class:`VersionedResource`."""

    changed: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description=(
            "The date and time of the last change to this resource."
        )
    )

    version: int = pydantic.Field(
        default=0
    )

    def new(
        self,
        *,
        status: str,
        generation: int,
        timestamp: datetime.datetime,
        message: str = '',
        **params: Any
    ) -> Any:
        raise NotImplementedError


class ResourceState(CurrentResourceState, Generic[C]):
    """Like :class:`CurrentResourceState`, but maintains the historical
    states.
    """
    model_config = {'populate_by_name': True}

    dirty: bool = pydantic.Field(
        default=False,
        exclude=True
    )

    conditions: list[C] = pydantic.Field(
        default_factory=list,
        description=(
            "Describes the state of the resource in reverse "
            "chronological order (the first item in the array is "
            "the first known state)."
        )
    )

    message: str | None = pydantic.Field(
        default=None,
        description=(
            "The message of the last known condition."
        )
    )

    current: str | None = pydantic.Field(
        default=None,
        description=(
            "The status of the last known condition."
        )
    )

    def _apply(self, condition: C, replay: bool = False) -> C:
        if self.is_final() and not replay:
            raise ValueError("Resource is in its final state.")
        if condition.timestamp == self.changed:
            condition.timestamp += datetime.timedelta(microseconds=1)
        self.changed = condition.timestamp
        self.message = condition.message
        self.current = condition.status
        if isinstance(condition.status, enum.Enum):
            self.current = condition.status.value
        self.apply(condition)
        if not replay:
            self.conditions.append(condition)
        if not replay:
            self.dirty = True
        return self.conditions[-1]

    def apply(self, condition: C) -> None:
        raise NotImplementedError

    def get_persistable_fields(self) -> set[str]:
        return set(ResourceState.model_fields.keys())

    def has(self, status: str) -> bool:
        return any([x.status == status for x in self.conditions])

    def model_post_init(self, _: Any) -> None:
        self.conditions = list(sorted(list(self.conditions), key=lambda x: x.timestamp.timestamp()))
        for condition in self.conditions:
            self._apply(condition, replay=True)

    def is_dirty(self) -> bool:
        return self.dirty

    def is_final(self) -> bool:
        return bool(self.conditions) and self.conditions[0].is_final()

    def new(
        self,
        *,
        status: str,
        generation: int,
        timestamp: datetime.datetime,
        message: str = '',
        **params: Any
    ) -> C:
        field = self.model_fields['conditions']
        adapter = cast(
            pydantic.TypeAdapter[list[C]],
            pydantic.TypeAdapter(field.annotation)
        )
        condition, *extra = adapter.validate_python([{
            **self.new_status_params(),
            **params,
            'message': message,
            'observed_generation': generation,
            'status': status,
            'timestamp': timestamp
        }])
        if extra:
            raise ValueError(f"{type(self).__name__}.new() creates one condition.")
        return self.update(condition)

    def new_status_params(self) -> dict[str, Any]:
        return {}

    def update(self, condition: C, replay: bool = False) -> C:
        return self._apply(condition, replay=replay)