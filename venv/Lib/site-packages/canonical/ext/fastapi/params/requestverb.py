# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Annotated
from typing import Literal
from typing import TypeAlias

import fastapi


VerbLiteral = Literal[
    "authorize",
    "create",
    "delete",
    "get",
    "inspect",
    "list",
    "replace",
    "update",
    "watch",
]


def get(request: fastapi.Request):
    return getattr(request.state, 'verb')


RequestVerb: TypeAlias = Annotated[VerbLiteral, fastapi.Depends(get)]