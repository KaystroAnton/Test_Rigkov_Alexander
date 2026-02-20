# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
import json
from typing import Any
from typing import Generic
from typing import TypeVar

import fastapi
import pydantic
import yaml


T = TypeVar('T', bound=pydantic.BaseModel)


class Response(fastapi.Response, Generic[T]):
    content: pydantic.BaseModel
    default_media_type: str | None = None
    model: type[T]

    @classmethod
    def typed(cls, model: type[T]) -> type['Response[T]']:
        return type(cls.__name__, (cls,), {'model': model})

    @functools.singledispatchmethod
    def render(self, content: pydantic.BaseModel | dict[str, Any] | str) -> bytes:
        if isinstance(content, pydantic.BaseModel):
            content = content.model_dump(mode='json', by_alias=True)
        media_type = self.media_type or self.default_media_type
        match media_type:
            case 'text/html':
                self.media_type = 'text/plain'
                return yaml.safe_dump( # type: ignore
                    data=content,
                    indent=2,
                    default_flow_style=False
                ).encode('utf-8') # type: ignore
            case 'application/yaml':
                return yaml.safe_dump( # type: ignore
                    data=content,
                    default_flow_style=False
                ).encode('utf-8') # type: ignore
            case _:
                return json.dumps(
                    content,
                    ensure_ascii=False,
                    allow_nan=False,
                    separators=(",", ":"),
                ).encode("utf-8")