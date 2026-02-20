# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import re
from typing import Any
from typing import Iterable

from pydantic_core import CoreSchema
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from pydantic import GetJsonSchemaHandler
from starlette.routing import compile_path # type: ignore
from starlette.routing import Convertor



class EndpointPath:

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=cls.__default_schema__(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.chain_schema([
                    cls.__default_schema__(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(str)
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _: CoreSchema,
        handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(cls.__default_schema__())

    @classmethod
    def __default_schema__(cls):
        return core_schema.str_schema(strip_whitespace=True)

    @classmethod
    def validate(cls, v: str):
        if str.startswith(v, '/'):
            raise ValueError(f'{cls.__name__} can not start with a slash: {v}.')
        return cls(*compile_path(v)) # type: ignore

    def __init__(
        self,
        pattern: re.Pattern[str],
        spec: str,
        params: dict[str, Convertor[Any]]
    ):
        self.pattern = pattern
        self.spec = spec
        self.params = params
        self.format_string = re.sub(r'\:{a-z}\}', '', self.spec)

    def construct(self, params: dict[str, Any]):
        if set(params.keys()) != set(self.params.keys()):
            raise TypeError("Missing parameters.")
        return self.format_string.format(**params)

    def match(self, path: str) -> None | dict[str, Any]:
        m = self.pattern.match(path)
        if m is None:
            return None
        params = m.groupdict()
        for k, v in params.items():
            params[k] = self.params[k].convert(v)
        return params

    def validate_keys(self, keys: Iterable[str]) -> bool:
        return set(self.params.keys()) == set(keys)

    def __str__(self):
        return self.spec

    def __repr__(self):
        return f'<EndpointPath: {self.spec}>'