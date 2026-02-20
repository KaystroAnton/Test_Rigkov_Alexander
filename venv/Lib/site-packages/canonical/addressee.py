# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Union

import pydantic

from .emailaddress import EmailAddress
from .honorific import HonorificEnum
from .phonenumber import Phonenumber
from .text import Text


AddresseeType = Union['PersonalAddressee', 'OrganizationAddressee']


class Addressee(pydantic.RootModel[AddresseeType]):

    @property
    def attention_name(self) -> str | None:
        return self.root.attention_name

    @property
    def display_name(self) -> str:
        return self.root.display_name


class OrganizationAddressee(pydantic.BaseModel):
    model_config = {'populate_by_name': True}

    organization_name: Text = pydantic.Field(
        default=...,
        alias='organizationName'
    )

    department: Text | None = pydantic.Field(
        default=None
    )

    attention: Union['PersonalAddressee', None] = pydantic.Field(
        default=None
    )

    email: EmailAddress | None = pydantic.Field(
        default=None
    )

    phonenumber: Phonenumber | str | None = pydantic.Field(
        default=None
    )

    @property
    def attention_name(self) -> str | None:
        return self.attention.display_name if self.attention else None

    @property
    def display_name(self) -> str:
        return self.organization_name


class PersonalAddressee(pydantic.BaseModel):
    model_config = {'populate_by_name': True}

    given_name: Text | None = pydantic.Field(
        default=None,
        alias='givenName'
    )

    family_name: Text = pydantic.Field(
        default=...,
        alias='familyName'
    )

    email: EmailAddress | None = pydantic.Field(
        default=None
    )

    phonenumber: Phonenumber | str | None = pydantic.Field(
        default=None
    )
    
    honorific: HonorificEnum | None = pydantic.Field(
        default=None
    )

    @property
    def attention_name(self) -> str | None:
        return None

    @property
    def display_name(self) -> str:
        if not self.given_name:
            return self.family_name
        return f'{self.given_name} {self.family_name}'


Addressee.model_rebuild()
OrganizationAddressee.model_rebuild()