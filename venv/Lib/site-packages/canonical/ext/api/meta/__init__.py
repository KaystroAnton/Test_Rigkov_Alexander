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
from typing import Generic
from typing import Literal
from typing import TypeVar
from typing import TYPE_CHECKING
from typing import Union

import pydantic
from pydantic.fields import FieldInfo

from ..types import APIVersion
if TYPE_CHECKING:
    from .. import APIResourceType
    from ..apiversioned import APIVersioned


T = TypeVar('T', bound=Union['APIResourceType', 'APIVersioned'])


class APIVersionedMeta(pydantic.BaseModel, Generic[T]):
    model_config = {'populate_by_name': True}
    _model: type[T] | None = pydantic.PrivateAttr(default=None)

    #api_version: str
    api_group: str = pydantic.Field(alias='group')
    #base_path: str
    kind: str
    namespaced: bool
    plural: str | None
    short: str | None = None
    version: str
    root: bool = False

    @property
    def api_version(self) -> APIVersion:
        v = f'{self.api_group}/{self.version}'\
            if self.api_group\
            else self.version
        return APIVersion(v)

    @property
    def base_path(self) -> str:
        p = f'{self.api_version}'
        if self.namespaced:
            p = f'{p}/namespaces/{{namespace}}'
        return f'{p}/{self.plural}'

    @property
    def cache_prefix(self):
        return f'{self.api_group or "core"}:{self.version}:{self.plural}'

    @property
    def model(self) -> type[T]:
        assert self._model
        return self._model

    def cache_key(self, name: str, namespace: str | None = None) -> str:
        if self.namespaced and namespace is None:
            raise TypeError("Namespace can not be None.")
        key = self.cache_prefix
        if namespace:
            key = f'{key}:{namespace}'
        return f'{key}:{name}'

    def contribute_to_class(
        self,
        cls: type[T],
        fields: dict[str, FieldInfo],
        root: tuple[type[Any], ...] | None = None
    ):
        setattr(cls, '__meta__', self)
        self._model = cls
        if fields:
            fields['api_version'].annotation = Literal[f'{self.api_version}']
            fields['api_version'].default = self.api_version
            fields['kind'].annotation = Literal[f'{self.kind}']
            fields['kind'].default = self.kind

    def get_url(self, detail: bool = False, subpath: str | None = None) -> str:
        path = f'{self.base_path}'
        if detail:
            path = f'{path}/{{name}}'
        path = f'/{path}'
        if subpath:
            path = f'{path}{subpath}'
        return path

    def is_namespaced(self) -> bool:
        return self.namespaced

    def reference(self, name: str, namespace: str | None = None):
        assert self._model is not None
        # TODO
        from ..objectreference import ObjectReference
        self.validate_namespace(namespace)
        ref = ObjectReference(
            api_version=self.api_version,
            kind=self.kind,
            name=name,
            namespace=namespace or ''
        )
        return ref.with_model(self._model)

    def validate_namespace(self, namespace: str | None):
        if not namespace and self.is_namespaced():
            raise TypeError(
                "The namespace parameter must be provided for "
                f"namespaced resources ({self._model.__name__})."
            )