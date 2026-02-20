# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
import operator
from functools import reduce
from typing import cast
from typing import Annotated
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Generic
from typing import Literal
from typing import Protocol
from typing import Self
from typing import TypeVar
from typing import TYPE_CHECKING

import pydantic
from pydantic.fields import FieldInfo

from canonical.exceptions import ProgrammingError
from .apimodel import APIModel
from .conditiontype import ConditionType
from .objectmeta import ObjectMeta
if TYPE_CHECKING:
    from .statefulresource import StatefulResource


C = TypeVar('C', bound=ConditionType[Any])
S = TypeVar('S', contravariant=True)
RESERVED_FIELDS: set[str] = {
    'name',
    'namespace',
    'uid'
}

ConditionList = Annotated[
    list[ConditionType[Any]],
    pydantic.Field(
        description=(
            "Conditions describe specific events related to this {kind}."
        ),
    )
]


class IHandler(Protocol, Generic[S]):
    def __call__(self, status: S, *args: Any) -> None: ...


class BaseResourceStatus(APIModel):
    _adapter: ClassVar[pydantic.TypeAdapter[Any]]
    _storage: ClassVar[pydantic.TypeAdapter[Any]]

    changed: datetime.datetime = pydantic.Field(
        default=...,
        description=(
            "The date and time of the last change to this {kind}."
        )
    )

    version: int = pydantic.Field(
        default=...,
        description=(
            "Current version of the {kind}."
        )
    )

    message: str = pydantic.Field(
        default=...,
        description="The message of the last known condition."
    )

    current: str = pydantic.Field(
        default=...,
        description="The status of the last known condition."
    )


class ResourceStatus(BaseResourceStatus):
    __abstract__: ClassVar[bool] = True
    _handlers: ClassVar[dict[str, tuple[ConditionType[Self], IHandler[Self]]]] = {}
    ClusterModel: ClassVar[type[ConditionType[Self]]]

    _resource: 'StatefulResource[Any, Any]' = pydantic.PrivateAttr(
        default=None
    )

    _dirty: bool = pydantic.PrivateAttr(
        default=False,
    )

    conditions: ConditionList

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def namespace(self) -> str:
        raise NotImplementedError

    @property
    def uid(self) -> int | str:
        raise NotImplementedError

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        reserved = set(cls.model_fields) & RESERVED_FIELDS
        if reserved:
            raise ProgrammingError(
                f"{cls.__name__} contains reserved fields: "
                f"{sorted(reserved)}"
            )
        if cls.__abstract__:
            cls.__abstract__ = False

        # Create a model for the conditions that includes
        # the UID of the Resource. This allows persistencee
        # in a different storage container (e.g. table).
        cls._handlers = {}
        cls._cluster_model = type( # type: ignore
            cls.__name__,
            (BaseResourceStatus,),
            {
                '__cluster__': True,
                '__annotations__': {
                    'namespace': str | None,
                    'name': str,
                    'uid': int | str
                }
            }
        )

    @classmethod
    def contribute_to_class(cls, parent: Any, attname: str, field: FieldInfo) -> None:
        for field in cls.model_fields.values():
            if field.description is None:
                continue
            field.description = str.format(field.description, kind=parent.__name__)
        assert cls.model_rebuild(force=True)

    @classmethod
    def default(cls) -> Self:
        raise NotImplementedError(
            f"{cls.__name__}.default() is not implemented. Subclasses "
            "must override this method to initialize the default "
            "state."
        )

    @classmethod
    def factory(cls, status: str, message: str | None = None, **kwargs: Any):
        now = datetime.datetime.now(datetime.timezone.utc)
        kwargs.setdefault('changed', now)
        kwargs.setdefault('conditions', [])
        kwargs.setdefault('current', status)
        kwargs.setdefault('message', message or '')
        kwargs.setdefault('version', 1)
        return cls.model_validate(kwargs)

    @classmethod
    def on(cls, status: str, *, title: str | None = None, **annotations: Any):
        """Create a function decorator that adds the specified `status`
        to the model with the given list of attributes `annotations`.
        """

        def decorator(func: Callable[..., None]) -> Callable[..., None]:
            reserved = set(annotations) & {'replay', *set(ConditionType.model_fields)}
            if reserved:
                raise ProgrammingError(
                    f"Handler {func.__name__} declares reserved fields: "
                    f"{sorted(reserved)}"
                )
            model = type('Condition', (ConditionType,), {
                'handle': staticmethod(func),
                'model_config': {
                    'populate_by_name': True,
                    'title': title or str.title(status) 
                },
                '__annotations__': {
                    **annotations,
                    'status': Literal[f'{status}']
                },
                '__handler_args__': set(annotations)
            })
            cls._handlers[status] = (cast(type[ConditionType[Self]], model), func) # type: ignore

            # Rebuild the .conditions field to include the new model so
            # that it is properly parsed and documented.
            models = [h[0] for h in cls._handlers.values()]

            annotation = model
            if len(models) > 1:
                annotation = reduce(operator.or_, models)
            cls.model_fields['conditions'].annotation = list[annotation]

            # Create an adapter to deserialize and serialize the storage
            # models for the conditions.
            cls._storage = pydantic.TypeAdapter(annotation)

            # Reinitialize the adapter and rebuild the model so that all
            # fields and validators are up-to-date.
            cls._adapter = pydantic.TypeAdapter(annotation)
            assert cls.model_rebuild(force=True)
            return func

        return decorator

    @pydantic.model_validator(mode='before')
    def preprocess(cls, values: dict[str, Any]):
        values.setdefault('conditions', [])
        return values

    @property
    def adapter(self) -> pydantic.TypeAdapter[ConditionType[Self]]:
        return self._adapter

    @property
    def resource(self) -> 'StatefulResource[ObjectMeta[Any], Any]':
        return self._resource

    def apply(self, status: str, **kwargs: Any):
        kwargs.setdefault('timestamp', datetime.datetime.now(datetime.timezone.utc))
        condition = self.adapter.validate_python({
            'status': status,
            'observed_generation': 1,
            #'observed_generation': self.resource.metadata.generation,
            **kwargs
        })
        self._apply(condition)

    def attach(self, resource: 'StatefulResource[Any, Any]'):
        self._resource = resource

    def clusterstate(self) -> Self:
        state = self._cluster_model.model_validate({
            **self.model_dump(exclude={'conditions'}),
            'name': self.resource.metadata.name,
            'namespace': self.resource.get_namespace(),
            'uid': self.resource.metadata.uid
        })
        return cast(Self, state)

    def is_dirty(self) -> bool:
        return self._dirty

    def is_final(self):
        return self.resource.is_final()

    def mark_dirty(self) -> None:
        self._dirty = True

    def model_dump_storage(self) -> dict[str, Any]:
        return self._storage.dump_python(self)

    def storage_model(self, data: Any) -> ConditionType[Self]:
        return self._storage.validate_python(data)

    def _apply(
        self,
        condition: ConditionType[Self],
        replay: bool = False
    ) -> ConditionType[Self]:
        if self.is_final() and not replay:
            raise ValueError("Resource is in its final state.")
        if condition.timestamp == self.changed:
            condition.timestamp += datetime.timedelta(microseconds=1)
        self.changed = condition.timestamp
        self.current = condition.status
        self.message = condition.message
        condition.observed_generation = self.resource.metadata.generation
        condition.apply(self)
        if not replay:
            self.conditions.append(condition)
        if not replay:
            self.mark_dirty()
        return condition