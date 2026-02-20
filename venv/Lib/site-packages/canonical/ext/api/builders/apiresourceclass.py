# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
from typing import cast
from typing import Annotated
from typing import Any
from typing import ClassVar
from typing import Literal
from typing import TYPE_CHECKING

import pydantic
from pydantic.fields import FieldInfo

from ..apimodelfieldinfo import APIModelFieldInfo
from ..apimodelinspector import APIModelInspector
from ..bases import BaseResourceDTO
from ..meta import APIVersionedMeta
from .apimodelclass import APIModelClassBuilder
if TYPE_CHECKING:
    from ..apiresource import APIResource
    from ..objectmeta import ObjectMeta


class APIResourceClassBuilder(APIModelClassBuilder['APIResource[Any]']):
    inspector = APIModelInspector()

    @property
    def api_version(self):
        return str.strip(f'{self.group}/{self.version}', '/')

    def __init__(
        self,
        group: str | None = None,
        version: str | None = None,
        plural: str | None = None,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        if self.abstract:
            return
        if group is None:
            raise TypeError("The `group` class parameter can not be None.")
        if version is None:
            raise TypeError("The `version` class parameter can not be None.")
        if plural is None:
            raise TypeError("The `plural` class parameter can not be None.")
        self.group = group
        self.models = self.inspector.get_models(self.model)
        self.plural = plural
        self.version = version

    def construct(self) -> None:
        if self.abstract:
            return
        self.set_field_annotation('api_version', Literal[f'{self.api_version}'])
        self.set_field_default('api_version', self.api_version)
        self.set_field_annotation('kind', Literal[f'{self.model.__name__}'])
        self.set_field_default('kind', self.model.__name__)
        if self.has_metadata():
            self.build_metadata()
        self.rebuild()
        super().construct()

    def setup_namespaced(self):
        """Make a resource namespaced."""
        pass

    def build_metadata(self) -> None:
        field, metadata_class = self.get_metadata_class()
        if self.namespaced:
            metadata_class = metadata_class.with_namespace()
            models = self.inspector.get_models(metadata_class) # type: ignore
            field.annotation = getattr(models, self.building)
            assert metadata_class.model_fields.get('namespace')
        self.metadata_class = self.model.__metadata_class__ = metadata_class

        # Build a descriptor model for the metadata to store it separately
        # from the model. This model should include the api_version
        # and kind fields.
        self.metadata_class.__stored_model__ = type('ObjectDescriptor', (self.metadata_class,), {
            'namespace': '',
            '__annotations__': {
                'api_version': Annotated[str, pydantic.Field()],
                'kind': Annotated[str, pydantic.Field()],
                'namespace': Annotated[str, pydantic.Field()],
            }
        })

    def get_metadata_class(self):
        field = self.fields['metadata']
        return field, cast('type[ObjectMeta[Any]]', field.annotation)

    def get_presentation_bases(self) -> tuple[type[Any]]:
        return BaseResourceDTO,

    def get_subclass_attrs(
        self,
        model: type[pydantic.BaseModel],
        mode: str,
        annotations: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return {
            **super().get_subclass_attrs(model, mode, annotations={
                **(annotations or {}),
                '__meta__': ClassVar[APIVersionedMeta[Any]]
            }),
            '__meta__': self.model.__meta__,
            'get_object_ref': self.model.get_object_ref,
            'key': cast('APIResource[Any]', model).key,
            'model': property(lambda _: self.model),
            'name': self.model.name,
        }

    def must_include_field(
        self,
        field: FieldInfo | APIModelFieldInfo,
        mode: str
    ):
        return not isinstance(field, APIModelFieldInfo) or field.is_included(mode)

    def on_representation_added(self, mode: str, model: type[APIResource[Any]]):
        model.model_fields['metadata'].annotation = self.subclass(
            model=self.metadata_class,
            mode=mode,
            attrs={},
            bases=(pydantic.BaseModel,)
        )
        assert model.model_rebuild(force=True)