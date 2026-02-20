# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import inspect
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import Self
from typing import TypeVar

import pydantic

from canonical.exceptions import ProgrammingError
from .objectmeta import ObjectMeta
from .resource import M
from .resource import Resource
from .resourcestatus import ResourceStatus


S = TypeVar('S', bound=ResourceStatus)


class StatefulResource(Resource[M], Generic[M, S]):
    _adapter: ClassVar[pydantic.TypeAdapter[Any]]

    status: S = pydantic.Field(
        default=...,
        description=(
            "The `status` field reports the current state of the resource. This "
            "value is modified by the system and can not be changed by clients. "
            "If the `.status` field is `null`, then the resource is created "
            "but no component or system has reported any state yet. Under "
            "normal circumstances, a state is set post-creation, and the "
            "absense of a state usually indicates an error."
        )
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        field = cls.model_fields['status']
        ResourceStatusImpl = field.annotation
        if not inspect.isclass(ResourceStatusImpl):
            return
        if not issubclass(ResourceStatusImpl, ResourceStatus):
            return
        cls._adapter = pydantic.TypeAdapter(ResourceStatusImpl)
        cls._status_model = ResourceStatusImpl
        assert cls.model_rebuild(force=True)

    @classmethod
    def has_state(cls) -> bool:
        return True

    @classmethod
    def model_validate_input(cls, data: dict[str, Any]) -> Self:
        data.setdefault('status', cls._status_model.default())
        return super().model_validate_input(data)

    @property
    def status_adapter(self) -> pydantic.TypeAdapter[S]:
        return self._adapter

    def clusterstate(self):
        assert self.status is not None
        return self.status.clusterstate()

    def initialize_status(self, status: S) -> None:
        pass

    def is_final(self) -> bool:
        return False

    def model_post_init(self, _: Any) -> None:
        super().model_post_init(_)
        self.status.attach(self)

    def _initialize_status(self, force: bool = False):
        self.status.attach(self)
        try:
            self.initialize_status(self.status)
        except pydantic.ValidationError as e:
            raise ProgrammingError(
                f"{type(self).__name__} raised an exception of "
                f"type {type(e).__name__}. Make sure that the "
                f"method {type(self).__name__}.initialize_status() "
                "is properly implemented."
            ) from e

    def _on_replaced(self, old: Self):
        super()._on_replaced(old)
        assert isinstance(self.metadata, ObjectMeta)
        assert isinstance(self.metadata.uid, str) or self.metadata.uid > 0
        self._initialize_status(force=True)