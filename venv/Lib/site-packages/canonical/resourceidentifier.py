# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Generic
from typing import TypeVar

from pydantic_core import core_schema
from pydantic_core import CoreSchema
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue


I = TypeVar('I')
T = TypeVar('T')


class ResourceIdentifier(Generic[I, T]):
    __module__: str = 'canonical'
    openapi_example: Any
    openapi_title: str


    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(max_length=128),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.chain_schema([
                    core_schema.union_schema([
                        core_schema.str_schema(),
                        core_schema.int_schema(),
                        core_schema.dict_schema()
                    ]),
                    core_schema.no_info_plain_validator_function(cls)
                ]),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(str)
        )

    @classmethod
    def __get_pydantic_json_schema__( # pragma: no cover
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue: # pragma: no cover
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema['examples'] = [cls.openapi_example]
        return json_schema

    def __eq__(self, key: object) -> bool: # pragma: no cover
        return all([
            isinstance(key, type(self)),
            hash(self) == hash(key)
        ])