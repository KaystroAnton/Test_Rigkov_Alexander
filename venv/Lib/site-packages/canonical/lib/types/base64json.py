# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from pydantic_core import CoreSchema
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from pydantic import GetJsonSchemaHandler

from canonical.lib.utils.encoding import b64decode_json
from canonical.lib.utils.encoding import b64encode_json


__all__: list[str] = [
    'Base64JSON'
]


class Base64JSON(dict[str, Any]):

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.chain_schema([
                    core_schema.union_schema([
                        core_schema.bytes_schema(max_length=0),
                        core_schema.str_schema(max_length=0)
                    ]),
                    core_schema.no_info_plain_validator_function(dict)
                ]),
                core_schema.chain_schema([
                    core_schema.union_schema([
                        core_schema.is_instance_schema(bytes),
                        core_schema.is_instance_schema(str),
                    ]),
                    core_schema.no_info_plain_validator_function(b64decode_json),
                    core_schema.dict_schema()
                ]),
                core_schema.dict_schema()
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(cls.serialize),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _: CoreSchema,
        handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())

    @staticmethod
    def serialize(value: dict[str, Any]) -> bytes:
        if not value:
            return b''
        return b64encode_json(value)