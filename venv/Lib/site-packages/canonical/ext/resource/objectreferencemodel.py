# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Generic
from typing import Literal
from typing import TypeVar
import pydantic


__all__: list[str] = [
    'ObjectReferenceModel'
]

T = TypeVar('T')


class ObjectReferenceModel(pydantic.BaseModel, Generic[T]):
    """Base class for object references."""
    model_config = {'populate_by_name': True}

    api_group: str = pydantic.Field(
        default=None,
        alias='apiGroup',
        title="API group",
        description=(
            "Specifies the API group of the referent. Cannot be updated."
        ),
        frozen=True
    )

    kind: str = pydantic.Field(
        default=...,
        description=(
            "Kind of the referent. Cannot be updated. In `CamelCase`."
        ),
        frozen=True
    )

    name: T = pydantic.Field(
        default=...,
        description=(
            "The `.metadata.name` of of the referent. Cannot be "
            "updated."
        ),
        frozen=True
    )

    def __init_subclass__(
        cls,
        api_group: str | None = None,
        kind: str | None = None,
        **kwargs: Any
    ) -> None:
        super().__init_subclass__()
        fields = cls.model_fields
        if api_group is not None:
            fields['api_group'].default = api_group
            fields['api_group'].annotation = Literal[f'{api_group}'] # type: ignore
        if kind is not None:
            fields['kind'].default = kind
            fields['kind'].annotation = Literal[f'{kind}'] # type: ignore
        cls.model_rebuild()
        cls.initialize_class(**kwargs)

    @classmethod
    def initialize_class(cls, **kwargs: Any):
        pass

    def is_local(self) -> bool:
        """Return a boolean indicating if the reference is to a local
        object i.e. on the same server. The default returns ``False``
        so that any local reference has to be explicitely implemented..
        """
        return False

    def get_namespace(self) -> str | None:
        return None

    def is_namespaced(self) -> bool:
        return False