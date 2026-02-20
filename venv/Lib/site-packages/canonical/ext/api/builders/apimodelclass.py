# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import copy
import inspect
from typing import cast
from typing import get_type_hints
from typing import Any
from typing import Generic
from typing import Literal
from typing import TypeVar
from typing import TYPE_CHECKING

import pydantic
from pydantic.fields import FieldInfo

from canonical.lib.protocols import IBuilder
from ..apimodelinspector import APIModelInspector
from ..apimodelfieldinfo import APIModelFieldInfo
if TYPE_CHECKING:
    from ..apimodel import APIModel


T = TypeVar('T', bound='APIModel')


class APIModelClassBuilder(IBuilder[T], Generic[T]):
    inspector = APIModelInspector()

    def __init__(
        self,
        model: type[T],
        metadata_class: type[pydantic.BaseModel] | None,
        abstract: bool = False,
        namespaced: bool = False,
        **kwargs: Any
    ) -> None:
        self.abstract = abstract
        self.building = model.__mode__
        self.metadata_class = metadata_class
        self.model = model
        self.namespaced = namespaced
        self.fields = model.model_fields

    def add_metadata_field(self, namespaced: bool) -> None:
        raise NotImplementedError

    def build_input_model(self):
        if self.building == 'domain' and self.inspector.is_concrete(self.model):
            self.model.__create_model__ = self.subclass(
                self.model, 'create', {}, name=f'{self.model.__name__}DTO'
            )
            self.on_representation_added('create', self.model.__create_model__)

    def construct(self) -> None:
        for name, field in dict(self.fields).items():
            self.model.contribute_to_class(self.model, name, field)
        if not getattr(self.model, '__create_model__', None):
            self.build_input_model()

    def contribute_annotations(self):
        """Iterate over the models' fields and find out it any of the fields is
        an APIModel and contribute them to the model.
        """
        # TODO: For now only support APIModel types itself, Union, List etc
        # comes later.
        for attname, field in self.fields.items():
            if not self.is_api_model_field(field):
                continue
            self.contribute_field(attname, field, field.annotation)

    def contribute_field(self, attname: str, field: FieldInfo, annotation: Any):
        annotation.contribute_to_class(self.model, attname, field)

    def get_presentation_bases(self) -> tuple[type[Any],]:
        return pydantic.BaseModel,

    def get_subclass_attrs(
        self,
        model: type[pydantic.BaseModel],
        mode: str,
        annotations: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return {
            'model_config': {**model.model_config, 'extra': 'ignore'},
            **copy.deepcopy(model.model_fields),
            '__annotations__': {
                **get_type_hints(model),
                **self.inspector.get_field_annotations(model),
                **(annotations or {})
            },
            '__metadata_class__': getattr(model, '__metadata_class__', None),
            '__mode__': mode,
            '__module__': model.__module__
        }

    def rebuild(self):
        assert self.model.model_rebuild(force=True)
        self.fields = self.model.model_fields

    def set_field_annotation(self, name: str, annotation: Any):
        self.fields[name].annotation = annotation
        self.rebuild()

    def set_field_default(self, name: str, default: Any):
        self.fields[name].default = default
        if self.fields[name].default_factory is not None:
            self.fields[name].default_factory = None

    def set_field_literal(self, name: str, value: str | list[str] | None, *values: Any):
        if value is None:
            self.set_field_annotation(name, str)
            return
        if not isinstance(value, list):
            value = [value]
        self.set_field_annotation(name, Literal[*tuple([*value, *values])]) # type: ignore

    def subclass(
        self,
        model: type[pydantic.BaseModel],
        mode: str,
        attrs: dict[str, Any],
        name: str | None = None,
        bases: tuple[type, ...] | None = None
    ) -> type[T]:
        """Subclass the configured model for the given presentation
        `mode`.
        """
        from ..apimodel import APIModel
        new_class = type(name or model.__name__, bases or self.get_presentation_bases(), {
            **attrs,
            **self.get_subclass_attrs(model, mode)
        })
        new_class = cast(type[pydantic.BaseModel], new_class)
        for name, field in set(model.model_fields.items()):
            if isinstance(field.annotation, TypeVar):
                raise TypeError(
                    "Can not create mode-specific implementations from "
                    f"generic classes (model: {model.__name__}, field: {name})."
                )
            if not isinstance(field, APIModelFieldInfo):
                continue
            if not field.is_included(mode):
                new_class.model_fields.pop(name, None)
                continue
            if inspect.isclass(field.annotation)\
            and issubclass(field.annotation, APIModel):
                new_field = new_class.model_fields[name]
                assert new_field.annotation
                models = self.inspector.get_models(new_field.annotation)
                new_field.annotation = getattr(models, mode)
        new_class.model_rebuild(force=True)
        return cast(type[T], new_class)

    def on_representation_added(self, mode: str, model: type[T]):
        pass

    async def build(self) -> T:
        raise NotImplementedError

    # Meta
    def is_api_model_field(self, field: FieldInfo):
        return inspect.isclass(field.annotation) and issubclass(field.annotation, self.model)

    def has_metadata(self) -> bool:
        return 'metadata' in self.fields