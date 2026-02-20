# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
import inspect
from typing import Any
from typing import ClassVar
from typing import Literal
from typing import Self
from typing import TypeVar
from typing import Union
from typing import TYPE_CHECKING

import pydantic
from pydantic.fields import FieldInfo

from .primarykey import PrimaryKey
if TYPE_CHECKING:
    from .objectmeta import ObjectMeta
    from .namespacedobjectmeta import NamespacedObjectMeta
    from .resource import Resource
    from .rootresource import RootResource


T = TypeVar('T', bound=pydantic.BaseModel)


class ResourceMeta(pydantic.BaseModel):
    _create_model: type[pydantic.BaseModel] = pydantic.PrivateAttr()
    input_excluded_fields: ClassVar[set[str]] = {'metadata', 'status'}
    api_group: str
    version: str
    kind: str
    namespaced: bool
    plural: str

    @classmethod
    def fromqualname(cls, model: type[Resource[Any] | RootResource[Any]], qualname: str):
        name, version = str.split(qualname, '/')
        if '.' in name:
            plural, group = name.split('.', 1)
        else:
            group = ''
            plural = name
        return cls(
            api_group=group,
            version=version,
            kind=model.__name__,
            namespaced=model.is_namespaced(),
            plural=plural
        )

    @property
    def api_version(self) -> str:
        return f'{self.api_group}/{self.version}'\
            if self.api_group\
            else self.version

    def contribute_to_class(
        self,
        cls: type[Resource[Any] | RootResource[Any]],
        fields: dict[str, FieldInfo],
        root: tuple[type[Resource[Any]], ...] | None = None
    ):
        cls.__meta__ = self
        cls.group = self.api_group
        cls.plural = self.plural
        base_path = self.api_group
        if base_path:
            base_path += '/'
        base_path = f'{base_path}{self.version}'
        if cls.is_namespaced():
            base_path += '/namespaces/{namespace}'
        cls.base_path = f'{base_path}/{self.plural}'

        # Set defaults and annotations.
        metadata_class = None
        if fields:
            fields['api_version'].annotation = Literal[f'{self.api_version}']
            fields['api_version'].default = self.api_version
            fields['kind'].annotation = Literal[f'{self.kind}']
            fields['kind'].default = self.kind

            # Find the metadata class
            metadata_class: Any = fields['metadata'].annotation
            if not inspect.isclass(metadata_class):
                raise NotImplementedError
            metadata_class.add_to_model(cls)
            assert cls.model_rebuild(force=True)
        cls.InputModel = self.build_input_model(cls, metadata_class, fields, root=root) # type: ignore

        cls.KeyType = PrimaryKey.typed(cls) # type: ignore
        #assert cls.model_rebuild(force=True)
        cls.__meta__ = self

    @classmethod
    def build_input_model(
        cls,
        model: type[T],
        meta: type['ObjectMeta[Any]'] | type['NamespacedObjectMeta[Any]'],
        fields: dict[str, FieldInfo],
        root: tuple[type[Resource[Any]], ...] | None = None
    ) -> Any:
        """Create an input model for the given resource implementation."""
        # The default implementation is to exclude the status for and
        # use a simplified ObjectMeta type.
        if root:
            return type(model.__name__, (pydantic.RootModel, ), { # type: ignore
                'model_config': model.model_config,
                '__annotations__': {'root': Union[*[model.InputModel for model in root]]} # type: ignore
            })

        # For Resources, simply create a subclass
        assert meta is not None
        fields = {
            k: v for k, v in fields.items()
            if k not in cls.input_excluded_fields
        }
        annotations: dict[str, Any] = {
            **{name: field.annotation for name, field in fields.items()},
            'metadata': meta.build_input_model(),
        }
        return type(model.__name__, (pydantic.BaseModel,), { # type: ignore
            'model_config': {
                **model.model_config,
                'title': f'Create{model.__name__}Request'
            },
            'metadata': meta.get_metadata_field(),
            '__annotations__': annotations,
            **fields
        })

    def update(self, resource: Any, metadata: Self | None, mode: Literal['replace', 'update']):
        pass