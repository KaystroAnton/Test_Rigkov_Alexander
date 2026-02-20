# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Iterable
from typing import TypeVar

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema
from pydantic_core import core_schema


T = TypeVar('T')


class DomainACL:
    __module__: str = 'canonical.security'

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> CoreSchema:
        schema = core_schema.union_schema([
            core_schema.chain_schema([
                core_schema.list_schema(),
                core_schema.no_info_plain_validator_function(cls.fromiterable)
            ]),
            core_schema.chain_schema([
                core_schema.none_schema(),
                core_schema.no_info_plain_validator_function(cls.null)
            ])   
        ])
        return core_schema.json_or_python_schema(
            json_schema=schema,
            python_schema=core_schema.union_schema([
                schema,
                core_schema.is_instance_schema(cls)
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.serialize())
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _: CoreSchema,
        handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.union_schema([
            core_schema.list_schema(),
            core_schema.none_schema()
        ]))

    @classmethod
    def fromiterable(cls, v: Iterable[str]) -> 'DomainACL':
        return cls(
            allow=[x for x in v if not str.startswith(x, '~')],
            deny=[x[1:] for x in v if str.startswith(x, '~')],
        )

    @classmethod
    def null(cls, v: None = None) -> 'DomainACL':
        return cls(None, None)

    def __init__(self, allow: Iterable[str] | None, deny: Iterable[str] | None) -> None:
        self._allow = None
        self._deny = None
        if allow is not None or deny is not None:
            self._allow = set(allow or [])
            self._deny = set(deny or [])

    def allows(self, domain: str) -> bool:
        return any([
            not self,
            all([
                self._allow is not None and 'ALL' in self._allow,
                any([
                    self._deny is None,
                    self._deny is not None and domain not in self._deny
                ])
            ]),
            all([
                self._allow is not None and domain in self._allow,
                self._deny is not None and domain not in self._deny
            ])
        ])

    def __bool__(self) -> bool:
        return bool(self._allow is not None or self._deny is not None)

    def serialize(self) -> list[str] | None:
        if not self:
            return None
        assert self._allow is not None
        assert self._deny is not None
        return [
            *[x for x in self._allow],
            *[f'~{x}' for x in self._deny]
        ]