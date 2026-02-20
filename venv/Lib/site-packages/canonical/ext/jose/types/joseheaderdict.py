# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import NotRequired
from typing import TypedDict


class JOSEHeaderDict(TypedDict):
    alg: str
    cty: NotRequired[str] | None
    crit: NotRequired[list[str]]
    jku: NotRequired[str | None]
    #jwk: JSONWebKey | None
    kid: NotRequired[str | None]
    typ: NotRequired[str | None]
    x5c: NotRequired[str | None]
    x5t: NotRequired[str | None]
    #x5t_sha256: str | None
    x5u: NotRequired[str | None]
    claims: NotRequired[dict[str, Any]]