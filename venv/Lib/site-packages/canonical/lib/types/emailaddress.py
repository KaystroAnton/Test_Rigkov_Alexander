# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable
from typing import TypeVar

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic.networks import validate_email
from pydantic_core import CoreSchema
from pydantic_core import core_schema

from .domainname import DomainName


T = TypeVar('T')


class EmailAddress(str):

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(max_length=320),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.chain_schema([
                    core_schema.str_schema(max_length=320),
                    core_schema.no_info_plain_validator_function(cls.fromstring)
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
        return handler(core_schema.str_schema(max_length=128))

    @classmethod
    def fromstring(cls, v: Any, _: Any = None) -> 'EmailAddress':
        v = str.lower(v)
        return cls(validate_email(v)[1]) # type: ignore

    @property
    def domain(self) -> DomainName:
        return DomainName(str.split(self, '@')[-1])

    @property
    def maskable(self) -> bytes:
        return str.encode(f'email:{self.lower()}', 'ascii')

    def mask(self, masker: Callable[[bytes], T]) -> T:
        return masker(self.maskable)

    def __repr__(self) -> str: # pragma: no cover
        return f'<EmailAddress: {str(self)}>'