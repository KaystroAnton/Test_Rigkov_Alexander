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
from typing import Generator

import iso3166
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema
from pydantic_core import core_schema


# Corrections for wrong names
COUNTRY_NAMES: dict[str, str] = {
    'NL': 'The Netherlands'
}

# Additional codes that are not in the iso3166 library (TODO: make issue at Github)
_records: list[iso3166.Country] = [
    # This one is problematic because it only has an ISO 3166 Alpha 2 code.
    iso3166.Country("Northern Ireland", "XI", 'GBR', '826', "Northern Ireland"),
]

# Another EU peculiarity: The European Commission generally uses
# ISO 3166-1 alpha-2 codes with two exceptions: EL (not GR) is
# used to represent Greece, and UK (not GB) is used to represent
# the United Kingdom.[10][11] This notwithstanding, the Official
# Journal of the European Communities specified that GR and GB be
# used to represent Greece and United Kingdom respectively.[12]
# For VAT administration purposes, the European Commission uses
# EL and GB for Greece and the United Kingdom respectively.
# https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2.
_eu_alpha2_mapping: dict[str, iso3166.Country] = {
    'EL': iso3166.countries_by_alpha2['GR'],
    'UK': iso3166.countries_by_alpha2['GB']
}

_alpha2_eu_mapping: dict[str, str] = {v.alpha2: k for k, v in _eu_alpha2_mapping.items()}

countries_by_alpha2: dict[str, iso3166.Country] = {
    x.alpha2: x
    for x in _records
}


class ISO3166Base(str):
    length: int

    @classmethod
    def __default_schema__(cls):
        return core_schema.str_schema(min_length=cls.length, max_length=cls.length)

    @classmethod
    def __get_pydantic_core_schema__(cls, *_: Any) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=cls.__default_schema__(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.chain_schema([
                    cls.__default_schema__(),
                    core_schema.no_info_plain_validator_function(cls.validate)
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
    def validate(cls, v: str, _: Any = None):
        try:
            return cls(cls._get_country(v))
        except LookupError:
            raise ValueError(f"Invalid code: {v}")

    @classmethod
    def _get_country(cls, v: str) -> str:
        raise NotImplementedError


class ISO3166Alpha2(ISO3166Base):
    length: int = 2

    @property
    def name(self) -> str:
        if str(self) in COUNTRY_NAMES:
            return COUNTRY_NAMES[self]
        c = iso3166.countries_by_alpha2.get(self)
        if c is None: # pragma: no cover
            raise LookupError
        return c.name

    @classmethod
    def _get_country(cls, v: str) -> str:
        c = countries_by_alpha2.get(v)\
            or iso3166.countries_by_alpha2.get(v)\
            or _eu_alpha2_mapping.get(v)
        if c is None:
            raise LookupError
        return c.alpha2