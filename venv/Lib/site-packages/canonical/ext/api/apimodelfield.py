# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable
from typing import Literal
from typing import NotRequired
from typing import TypedDict
from typing import Unpack

from pydantic import Field
from pydantic.fields import AliasChoices
from pydantic.fields import AliasPath
from pydantic.fields import JsonDict
from pydantic.fields import PydanticUndefined
from pydantic.fields import PydanticUndefined
from pydantic.types import Discriminator

from .apimodelfieldinfo import APIModelFieldInfo


_Unset: Any = PydanticUndefined


class APIModelFieldParams(TypedDict):
    default_factory: NotRequired[Callable[[], Any] | None]
    alias: NotRequired[str | None]
    alias_priority: NotRequired[int | None]
    validation_alias: NotRequired[str | AliasPath | AliasChoices | None]
    serialization_alias: NotRequired[str | None]
    title: NotRequired[str | None]
    description: NotRequired[str | None]
    examples: NotRequired[list[Any] | None]
    exclude: NotRequired[bool | None]
    discriminator: NotRequired[str | Discriminator | None]
    json_schema_extra: NotRequired[JsonDict | Callable[[JsonDict], None] | None]
    frozen: NotRequired[bool | None]
    validate_default: NotRequired[bool | None]
    repr: NotRequired[bool]
    init_var: NotRequired[bool | None]
    kw_only: NotRequired[bool | None]
    pattern: NotRequired[str | None]
    strict: NotRequired[bool | None]
    gt: NotRequired[float | None]
    ge: NotRequired[float | None]
    lt: NotRequired[float | None]
    le: NotRequired[float | None]
    multiple_of: NotRequired[float | None]
    allow_inf_nan: NotRequired[bool | None]
    max_digits: NotRequired[int | None]
    decimal_places: NotRequired[int | None]
    min_length: NotRequired[int | None]
    max_length: NotRequired[int | None]
    union_mode: NotRequired[Literal['smart', 'left_to_right']]


def APIModelField(
    default: Any = PydanticUndefined,
    *,
    when: set[Literal['create', 'update', 'store', 'view']] | None = _Unset,
    encrypt: bool = False,
    **kwargs: Unpack[APIModelFieldParams]
) -> Any:
    return APIModelFieldInfo.from_field_info(
        field=Field(default=default, **kwargs),
        encrypt=encrypt,
        when=when
    )