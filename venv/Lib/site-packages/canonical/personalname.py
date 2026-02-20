# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .text import Text


class PersonalName(pydantic.BaseModel):
    model_config = {'populate_by_name': True}

    given_name: Text | None = pydantic.Field(
        default=None,
        alias='givenName',
        description=(
            "Given name(s) or first name(s). Note that in some cultures, "
            "people can have multiple given names; all can be present, "
            "with the names being separated by space characters."
        )
    )

    family_name: Text = pydantic.Field(
        default=...,
        alias='familyName',
        description=(
            "Surname(s) or last name(s). Note that in some cultures, people "
            "can have multiple family names or no family name; all can be "
            "present, with the names being separated by space characters.\n\n"
            "If there is no surname, then this field is considered the name and "
            "the `givenName` field must be empty."
        )
    )

    @property
    def display_name(self):
        if not self.given_name:
            return self.family_name
        return f'{self.given_name} {self.family_name}'

    def __str__(self):
        return self.display_name