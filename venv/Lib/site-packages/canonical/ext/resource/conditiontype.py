# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
import inspect
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import TypeVar
from typing import TYPE_CHECKING

import pydantic

from canonical.exceptions import ProgrammingError
if TYPE_CHECKING:
    from .resourcestatus import ResourceStatus


R = TypeVar('R')
S = TypeVar('S', bound='ResourceStatus[Any]')
RESERVED_FIELDS: set[str] = {'uid', 'namespace', 'name', 'parent'}


class ConditionType(pydantic.BaseModel, Generic[S]):
    """Describes the condition of a :class:`VersionedResource`."""
    model_config = {'populate_by_name': True}
    StorageModel: ClassVar[type[pydantic.BaseModel]]
    __handler_args__: ClassVar[set[str]]
    __storage__: ClassVar[bool] = False
    _can_replay: ClassVar[bool] = False
    _uid: int | None = pydantic.PrivateAttr(default=None)

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

    status: str = pydantic.Field(
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

    @property
    def uid(self):
        return self._uid

    def __init_subclass__(cls, **kwargs: Any):
        return super().__init_subclass__()

    @classmethod
    def __pydantic_init_subclass__(cls, status: str | None = None, **kwargs: Any) -> None:
        reserved = set(cls.model_fields) & RESERVED_FIELDS
        if reserved and not cls.__storage__:
            raise ProgrammingError(
                f"{cls.__name__} contains reserved fields: "
                f"{sorted(reserved)}."
            )

        # Determine which arguments the handler accepts.
        if inspect.ismethod(cls.handle):
            raise ProgrammingError(
                f'Subclasses must override {cls.__name__}.handle().'
            )

        sig = inspect.signature(cls.handle)
        if 'replay' in sig.parameters:
            if sig.parameters['replay'].annotation != bool:
                raise ProgrammingError(
                    "The `replay` argument must be annotated as a boolean "
                    "(replay: bool). This parameter is passed in via the "
                    "base class and indicates if a condition is being "
                    "replayed."
                )
            cls._can_replay = True

        # TODO: Do not hardcode the identifier type.
        if not cls.__storage__:
            cls.StorageModel = type(
                cls.__name__,
                (cls,),
                {
                    '__annotations__': {
                        'name': str,
                        'namespace': str | None,
                        'parent': int,
                        'uid': int,
                    },
                    '__storage__': True
                }
            )

    @classmethod
    def can_replay(cls) -> bool:
        return cls._can_replay

    def handle(self, state: S, **kwargs: Any) -> None:
        raise NotImplementedError

    def apply(self, state: S, replay: bool = False) -> None:
        kwargs = self.model_dump(include=self.__handler_args__)
        if self.can_replay():
            kwargs['replay'] = replay
        return self.handle(state, **kwargs)

    def can_transition(self, state: S):
        return True

    def is_dirty(self):
        return self._uid is None

    def is_final(self) -> bool:
        return False