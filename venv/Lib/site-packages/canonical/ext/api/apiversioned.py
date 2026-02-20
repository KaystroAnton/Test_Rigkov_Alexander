# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import ClassVar
from typing import Self

from .apimodel import APIModel
from .apiversionedmeta import APIVersionedMeta
from .fields import APIVersion
from .fields import Kind
from .registry import register


__all__: list[str] = [
    'APIVersioned'
]


class APIVersioned(APIModel, abstract=True):
    __abstract__ = True
    __descriptor_class__: ClassVar[type[APIVersionedMeta[Self]]] = APIVersionedMeta
    __meta__: ClassVar[APIVersionedMeta[Any]]
    api_version: APIVersion
    kind: Kind

    @classmethod
    def __pydantic_init_subclass__(
        cls,
        namespaced: bool = False,
        descriptor: type[APIVersionedMeta[Self]] | None = None,
        api_version: str | None = None,
        group: str | None = None,
        version: str | None = None,
        kind: str | None = None,
        plural: str | None = None,
        short: str | None = None,
        **kwargs: Any
    ):
        meta: APIVersionedMeta[Any] | None = getattr(cls, '__meta__', None)
        if descriptor is not None:
            cls.__descriptor_class__ = descriptor
        if meta:
            kwargs.update({
                'group': meta.api_group,
                'plural': meta.plural,
                'version': meta.version
            })
        super().__pydantic_init_subclass__(namespaced=namespaced, **kwargs)

    def __init_subclass__(
        cls,
        group: str | None = None,
        version: str | None = None,
        kind: str | None = None,
        plural: str | None = None,
        short: str | None = None,
        namespaced: bool = False,
        **kwargs: Any
    ):
        if (group is not None and version is not None)\
        and not kwargs.get('abstract'):
            meta = cls.__descriptor_class__( # type: ignore
                group=group,
                version=version,
                kind=kind or cls.__name__,
                plural=plural,
                short=short,
                namespaced=namespaced,
            )
            meta.contribute_to_class(cls, cls.model_fields)
            assert hasattr(cls, '__meta__')
            register(cls.__meta__)
        return super().__init_subclass__(namespaced=namespaced, **kwargs)

    def has_state(self) -> bool:
        raise NotImplementedError