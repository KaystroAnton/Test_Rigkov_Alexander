# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .iso3166 import ISO3166Alpha2
from .text import Text


class BaseAddress(pydantic.BaseModel):
    model_config = {'populate_by_name': True}

    address1: Text = pydantic.Field(
        default=...
    )

    address2: Text | None = pydantic.Field(
        default=None
    )

    address3: Text | None = pydantic.Field(
        default=None
    )

    city: Text = pydantic.Field(
        default=...
    )

    postal_code: Text = pydantic.Field(
        default=...,
        alias='postalCode'
    )

    country_code: ISO3166Alpha2 = pydantic.Field(
        default=...,
        alias='countryCode'
    )