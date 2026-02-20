# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal

import pydantic



EncodingLiteral = Literal[
    'base64',
    'hex',
    'utf-8',
]


KindLiteral = Literal[
    'body',
    'headers',
    #'json',
    'query',
]


class HTTPRequestRef(pydantic.BaseModel):
    kind: KindLiteral = pydantic.Field(
        default=...,
        description=(
            "Specifies the component of the HTTP request that "
            "is being referenced."
        )
    )

    name: str = pydantic.Field(
        default='',
        description=(
            "Indicates where to find the the referent.\n\n"
            "- For `body`, this field is ignored.\n\n"
            "- For `headers` and `query`, the `name` field."
            "indicates the name of the header or query parameter.\n\n"
            "Note that when `kind=query`, repeated query parameters "
            "are parsed as a list and the `encoding` is applied to "
            "each member in the list."
        )
    )

    encoding: EncodingLiteral = pydantic.Field(
        default=...,
        description=(
            "The content encoding of the referent."
        )
    )

    def model_post_init(self, _: Any) -> None:
        if self.kind != 'body' and not self.name:
            raise ValueError("The `.name` field is required.")