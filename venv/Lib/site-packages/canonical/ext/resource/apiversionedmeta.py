# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import Literal
from typing import TypeVar
from typing import Union
from typing import TYPE_CHECKING

import pydantic
from pydantic.fields import FieldInfo

from .apimodelinspector import APIModelInspector
if TYPE_CHECKING:
    from .apimodel import APIModel
    from .apiversioned import APIVersioned
    from .resource import Resource
    from .rootresource import RootResource


T = TypeVar('T', bound=Union['APIModel', 'Resource[Any]', 'RootResource[Any]'])


class APIVersionedMeta(pydantic.BaseModel, Generic[T]):
    inspector: ClassVar[APIModelInspector] = APIModelInspector()
    _model: type[T] | None = pydantic.PrivateAttr(default=None)
    api_version: str
    api_group: str
    base_path: str
    version: str
    kind: str
    namespaced: bool
    plural: str

    @classmethod
    def fromqualname(
        cls,
        model: type[APIVersioned],
        api_version: str,
        **kwargs: Any
    ):
        name, version = str.split(api_version, '/')
        if '.' in name:
            plural, group = name.split('.', 1)
        else:
            group = ''
            plural = name
        base_path = group
        if base_path:
            base_path += '/'
        base_path = f'{base_path}{version}'
        if cls.inspector.is_namespaced(model):
            base_path += '/namespaces/{namespace}'
        cls.base_path = f'{base_path}/{plural}'
        return cls(
            api_version=api_version,
            api_group=group,
            base_path=base_path,
            version=version,
            kind=model.__name__,
            namespaced=cls.inspector.is_namespaced(model),
            plural=plural
        )

    @property
    def model(self) -> type[T]:
        assert self._model
        return self.model

    def contribute_to_class(
        self,
        cls: type[T],
        fields: dict[str, FieldInfo],
        root: tuple[type[Any], ...] | None = None
    ):
        setattr(cls, '__meta__', self)
        if fields:
            fields['api_version'].annotation = Literal[f'{self.api_version}']
            fields['api_version'].default = self.api_version
            fields['kind'].annotation = Literal[f'{self.kind}']
            fields['kind'].default = self.kind