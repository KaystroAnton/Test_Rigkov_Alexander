# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal

import pydantic

from .addressee import Addressee
from .baseaddress import BaseAddress


class Address(BaseAddress):
    model_config = {'populate_by_name': True}

    kind: Literal['Address'] = pydantic.Field(
        default='Address'
    )

    addressee: Addressee | None = pydantic.Field(
        default=None
    )

    remarks: str | None = pydantic.Field(
        default=None
    )
