# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import cast
from typing import Any
from typing import Literal

from pydantic.fields import FieldInfo


class APIModelFieldInfo(FieldInfo):
    __slots__ = (*FieldInfo.__slots__, 'when', 'encrypt')

    @classmethod
    def from_annotation(cls, annotation: type[Any]) -> FieldInfo:
        raise NotImplementedError

    @classmethod
    def from_annotated_attribute(cls, annotation: type[Any], default: Any) -> FieldInfo:
        raise NotImplementedError

    @classmethod
    def from_field(cls, *args: Any, **kwargs: Any): # type: ignore
        raise NotImplementedError

    @classmethod
    def from_field_info(cls, field: FieldInfo, **kwargs: Any):
        kwargs.update({
            k: getattr(field, k) for k in field.__slots__
            if not str.startswith(k, '_')
        })
        return cls(**kwargs)

    @classmethod
    def merge_field_infos(cls, *field_infos: FieldInfo, **overrides: Any): # type: ignore
        """Merge `FieldInfo` instances keeping only explicitly set attributes.

        Later `FieldInfo` instances override earlier ones.

        Returns:
            FieldInfo: A merged FieldInfo instance.
        """
        flattened_field_infos: list[FieldInfo] = []
        for field_info in field_infos:
            flattened_field_infos.extend(x for x in field_info.metadata if isinstance(x, FieldInfo))
            flattened_field_infos.append(field_info)
        field_infos = tuple(flattened_field_infos)
        new_kwargs: dict[str, Any] = {}
        metadata = {}
        for field_info in field_infos:
            new_kwargs.update(field_info._attributes_set)
            for x in field_info.metadata:
                if not isinstance(x, FieldInfo):
                    metadata[type(x)] = x
        new_kwargs.update(overrides)
        field_info = cls(**new_kwargs)
        field_info.metadata = list(cast(Any, metadata.values()))
        assert isinstance(field_info, APIModelFieldInfo)
        return field_info

    def __init__(
        self,
        when: set[Literal['create', 'update', 'store', 'view']] | None = None,
        encrypt: bool = False,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.encrypt = encrypt
        self.when = when or set()

    def is_included(self, mode: str) -> bool:
        return bool(self.when) and mode in self.when