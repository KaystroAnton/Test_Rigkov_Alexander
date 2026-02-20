# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
from typing import NotRequired
from typing import TypedDict

from canonical.lib.types import EmailAddress
from .audiencetype import AudienceType


class JWTDict(TypedDict):
    iss: NotRequired[str]
    sub: NotRequired[str]
    aud: NotRequired[AudienceType]
    exp: NotRequired[int]
    nbf: NotRequired[int]
    iat: NotRequired[int]
    jti: NotRequired[str]
    name: NotRequired[str]
    given_name: NotRequired[str]
    family_name: NotRequired[str]
    middle_name: NotRequired[str]
    nickname: NotRequired[str]
    preferred_username: NotRequired[str]
    profile: NotRequired[str]
    picture: NotRequired[str]
    website: NotRequired[str]
    email: NotRequired[EmailAddress]
    email_verified: NotRequired[bool]
    gender: NotRequired[str]
    birthdate: NotRequired[datetime.date | str]
    zoneinfo: NotRequired[str]
    locale: NotRequired[str]
    phone_number: NotRequired[str]
    phone_number_verified: NotRequired[str]
    address: NotRequired[str]
    updated_at: NotRequired[int]
    azp: NotRequired[str]
    nonce: NotRequired[str]
    auth_time: NotRequired[str]
    at_hash: NotRequired[str]
    c_hash: NotRequired[str]
    acr: NotRequired[str]
    amr: NotRequired[list[str]]
    #sub_jwk: NotRequired[str]