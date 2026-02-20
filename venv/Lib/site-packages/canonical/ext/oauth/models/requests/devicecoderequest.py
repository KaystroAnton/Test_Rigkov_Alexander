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

from .grantmodel import GrantModel


class DeviceCodeRequest(GrantModel[Literal['urn:ietf:params:oauth:grant-type:device_code']]):
    device_code: str = pydantic.Field(
        default=...,
        title="Device Code",
        description=(
            "The device verification code, `device_code` "
            "from the device authorization response"
        )
    )