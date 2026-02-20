# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .emailaddress import EmailAddress
from .honorific import HonorificEnum
from .phonenumber import Phonenumber


class DeliveryContact(pydantic.BaseModel):
    """Describes a person that may be contacted in the context of a
    delivery.
    """
    model_config = {'populate_by_name': True}

    name: str = pydantic.Field(
        default=...
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
    def display_name(self) -> str:
        return self.name