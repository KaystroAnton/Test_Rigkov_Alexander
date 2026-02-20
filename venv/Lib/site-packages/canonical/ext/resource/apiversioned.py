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


__all__: list[str] = [
    'APIVersioned'
]


class APIVersioned(APIModel, abstract=True):
    __abstract__ = True
    __descriptor_class__: ClassVar[type[APIVersionedMeta[Self]]] = APIVersionedMeta
    __meta__: ClassVar[Any]
    api_version: APIVersion
    kind: Kind

    @classmethod
    def __pydantic_init_subclass__(
        cls,
        descriptor: type[APIVersionedMeta[Self]] | None = None,
        api_version: str | None = None,
        **kwargs: Any
    ):
        meta: APIVersionedMeta[Any] | None = getattr(cls, '__meta__', None)
        if meta is not None:
            kwargs.update({
                'group': meta.api_group,
                'plural': meta.plural,
                'version': meta.version
            })
        if descriptor is not None:
            cls.__descriptor_class__ = descriptor
        if api_version is not None:
            assert meta is None
            meta = cls.__descriptor_class__.fromqualname(
                model=cls,
                api_version=api_version,
                **kwargs
            )
            meta.contribute_to_class(cls, cls.model_fields)
        super().__pydantic_init_subclass__(**kwargs)

    def has_state(self) -> bool:
        raise NotImplementedError