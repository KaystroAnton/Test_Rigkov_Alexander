# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import re
from typing import Any
from typing import TypeVar

from pydantic_core import CoreSchema
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from pydantic import GetJsonSchemaHandler


T = TypeVar('T')


class StringType(str):
    """Base class for string types."""
    __module__: str = 'canonical'
    lowercase: bool = False
    max_length: int | None = None
    min_length: int | None = None
    openapi_title: str | None = None
    openapi_format: str | None = None
    patterns: re.Pattern[Any] | list[re.Pattern[Any]] = []
    pattern: str | None = None
    strip_whitespace: bool = True

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=cls.__default_schema__(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.chain_schema([
                    cls.__default_schema__(),
                    core_schema.no_info_plain_validator_function(cls.transform),
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
        return core_schema.str_schema(
            max_length=cls.max_length,
            min_length=cls.min_length,
            pattern=cls.pattern,
            strip_whitespace=cls.strip_whitespace,
            to_lower=cls.lowercase
        )

    @classmethod
    def transform(cls, v: str) -> str:
        return v

    @classmethod
    def validate(cls, v: str) -> str:
        return cls(v)

    @classmethod
    def validate_pattern(cls, v: Any, _: Any = None) -> str:
        if not isinstance(v, str):
            raise ValueError(f"{cls.__name__} must be instantiated from a string type.")
        patterns = cls.patterns
        if not isinstance(patterns, list): # pragma: no cover
            patterns = [patterns]
        for pattern in patterns:
            if not pattern.match(v):
                raise ValueError(f"not a valid {cls.__name__}.")
        return v

    def __new__(cls, object: object):
        self = super().__new__(cls, object=object)
        self.type_post_init()
        return self

    def type_post_init(self):
        pass

    def __repr__(self) -> str: # pragma: no cover
        return f'<{type(self).__name__}: {str(self)}>'