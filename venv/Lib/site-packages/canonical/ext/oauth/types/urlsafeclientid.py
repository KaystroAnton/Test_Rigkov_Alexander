# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import cast
from typing import Any
from typing import ClassVar
from typing import Self

from pydantic_core import CoreSchema
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from pydantic import GetJsonSchemaHandler

from canonical.ext.api import get_meta
from canonical.ext.api import APIResourceType
from canonical.ext.api.protocols import IObjectIdentifier
from canonical.lib.utils.encoding import b64decode
from canonical.lib.utils.encoding import b64encode


class URLSafeClientID:
    supported_types: ClassVar[set[str]] = {
        'clusterclients'
    }
    version: str
    plural: str
    namespace: str
    name: str

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.chain_schema([
                    core_schema.is_instance_schema(str),
                    core_schema.no_info_plain_validator_function(cls.fromstring),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(cls.encode)
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _: CoreSchema,
        handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())

    @classmethod
    def encode(cls, self: Self | str):
        if isinstance(self, str):
            return self
        return b64encode(f'{self.version}:{self.plural}:{self.namespace}:{self.name}', encoder=str)

    @classmethod
    def fromstring(cls, v: str):
        try:
            version, plural, namespace, name = str.split(b64decode(v, str), ':')
            if version != '1':
                raise ValueError
            if plural not in cls.supported_types:
                raise ValueError
            return cls(version, plural, namespace, name)
        except ValueError:
            raise ValueError("Invalid Client ID.")

    @property
    def cache_key(self) -> str:
        return self.meta.cache_key(self.name, self.namespace or None)

    @property
    def meta(self):
        return get_meta('oauth/v2', plural=self.plural)

    @property
    def model(self):
        return self.meta.model

    @property
    def ref(self) -> IObjectIdentifier[APIResourceType]:
        return cast(
            IObjectIdentifier[APIResourceType],
            self.meta.reference(self.name, namespace=self.namespace or None)
        )

    def __init__(self, version: str, plural: str, namespace: str, name: str):
        self.version = version
        self.plural = plural
        self.namespace = namespace
        self.name = name

    def __repr__(self):
        return (
            f"<URLSafeClientID({repr(self.version)}, {repr(self.plural)}, "
            f"{repr(self.namespace)}, {repr(self.name)})"
        )

    def __str__(self) -> str:
        return self.encode(self)