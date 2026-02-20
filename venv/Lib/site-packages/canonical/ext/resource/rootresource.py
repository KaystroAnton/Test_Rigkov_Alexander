# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import get_args
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import Literal
from typing import Self
from typing import TypeAlias
from typing import TypeVar

import pydantic

from canonical.ext.api import ObjectReference
from .apiresourcelist import APIResourceList
from .listbase import ListBase
from .resource import Resource
from .resourcemeta import ResourceMeta

__all__: list[str] = [
    'RootResource'
]

T = TypeVar('T', bound=Resource[Any])
S = TypeVar('S', bound='RootResource[Any]')


class RootResource(pydantic.RootModel[T], Generic[T]):
    __version__: ClassVar[str]

    _is_namespaced: bool
    group: ClassVar[str]
    base_path: ClassVar[str]
    plural: ClassVar[str]
    List: ClassVar[type[ListBase[Any, Any]]]
    InputModel: ClassVar[type[Self]]
    __meta__: ClassVar[ResourceMeta]

    @property
    def api_version(self):
        return self.root.api_version

    @property
    def key(self):
        ref = ObjectReference(
            api_version=self.api_version,
            kind=self.kind,
            name=self.metadata.name,
            namespace=self.metadata.get_namespace() or '',
            resource_version=self.metadata.resource_version or '',
            uid=self.metadata.uid
        )
        return ref.attach(self.metadata).with_model(type(self))

    @property
    def kind(self):
        return self.root.kind

    @property
    def metadata(self):
        return self.root.metadata

    @property
    def relname(self):
        return self.root.relname

    @classmethod
    def register(cls, resources: APIResourceList):
        return resources.add(cls.__meta__)

    def __init_subclass__(
        cls,
        version: str | None = None,
        namespaced: bool | None = None,
        **kwargs: Any
    ):
        super().__init_subclass__()
        paths: set[str] = set()
        types: tuple[type[Resource[Any]]] = get_args(cls.model_fields['root'].annotation) # type: ignore
        if version:
            assert len(types)
            cls._is_namespaced = types[0].is_namespaced()
            meta = ResourceMeta.fromqualname(cls, version)
            for t in types:
                t.add_to_root(cls, meta)
            meta.contribute_to_class(cls, {}, root=types)
            return
        for model in types:
            paths.add(model.base_path)
        if len(paths) > 1:
            raise ValueError(f"All root models must have the same base path.")
        if paths:
            assert len(types) > 1
            cls.base_path = types[0].base_path
            cls.group = types[0].group
            cls.plural = types[0].plural
            cls._is_namespaced = types[0].is_namespaced()
            cls.KeyType = PrimaryKey.typed(cls) # type: ignore
            cls.__meta__ = ResourceMeta.model_validate({
                **types[0].__meta__.model_dump(),
                'kind': cls.__name__
            })
        cls.List = type(f'{cls.__name__}List', (ListBase[Literal[f'{cls.__name__}List'], cls],), {
            'items': pydantic.Field(
                default_factory=list,
                description=(
                    "The `items` member contains an array "
                    f"of `{cls.__name__}` objects."
                )
            ),
            '__annotations__': {'items': list[cls]}
        })
        cls.List.model_fields['kind'].default = f'{cls.__name__}List'
        cls.List.model_rebuild()

        cls.model_config.update({
            'title': cls.__name__
        })
        cls.model_rebuild()

    @classmethod
    def is_destroyable(cls) -> bool:
        return True

    @classmethod
    def is_namespaced(cls) -> bool:
        return cls._is_namespaced

    @classmethod
    def is_purgable(cls) -> bool:
        return True

    @classmethod
    def model_validate_input(cls, data: dict[str, Any]) -> Self:
        return cls.model_validate(data)

    def can_change(self, old: T) -> bool:
        return self.root.can_change(old)

    def get_comparison_fields(self) -> set[str]:
        return self.root.get_comparison_fields()

    def get_namespace(self) -> str | None:
        return self.root.get_namespace()

    def has_state(self):
        return self.root.has_state()

    def in_namespace(self, namespace: str | None):
        return self.root.in_namespace(namespace)

    def is_consistent(self) -> bool:
        return self.root.is_consistent()

    def model_dump_yaml(self, **kwargs: Any):
        return self.root.model_dump_yaml(**kwargs)

    def replacable(self) -> bool:
        return self.root.replacable()

    async def persist(self, *args: Any, **kwargs: Any):
        obj = await self.root.persist_key(self.key, *args, **kwargs)

        # Ensure that the same type is returned.
        return self.model_validate(obj.model_dump())


ResourceType: TypeAlias = Resource[Any] | RootResource[Any]
ResourceTypeVar = TypeVar('ResourceTypeVar', bound=ResourceType)