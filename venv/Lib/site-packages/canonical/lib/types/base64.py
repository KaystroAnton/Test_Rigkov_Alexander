# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Self

from pydantic_core import CoreSchema
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from pydantic import GetJsonSchemaHandler

from canonical.lib.utils.encoding import b64decode
from canonical.lib.utils.encoding import b64encode


__all__: list[str] = [
    'Base64'
]


class Base64(bytes):

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.chain_schema([
                core_schema.union_schema([
                    core_schema.is_instance_schema(bytes),
                    core_schema.chain_schema([
                        core_schema.is_instance_schema(str),
                        core_schema.no_info_plain_validator_function(cls.b64decode),
                        core_schema.no_info_plain_validator_function(cls.validate)
                    ])
                ]),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls.b64encode
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _: CoreSchema,
        handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())

    @classmethod
    def b64decode(cls, value: str):
        return b64decode(value)

    @classmethod
    def b64encode(cls, value: str):
        return  b64encode(value, encoder=bytes.decode)

    @classmethod
    def validate(cls, instance: Self):
        return instance