# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from canonical import Text


class UOM(pydantic.BaseModel):
    model_config = {'populate_by_name': True}    

    key: Text = pydantic.Field(
        default=...,
        description=(
            "A global identifier for the represented unit of measurement."
        )
    )

    display_name: Text = pydantic.Field(
        default=...,
        alias='displayName',
        description=(
            "The human-readable display name for the unit of "
            "measurement."
        )
    )

    @classmethod
    def each(cls):
        return cls.model_validate({
            'key': 'each',
            'display_name': 'Each'
        })