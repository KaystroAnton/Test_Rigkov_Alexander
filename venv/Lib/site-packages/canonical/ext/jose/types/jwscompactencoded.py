# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import TypeVar

import pydantic

from canonical.lib.types import StringType


M = TypeVar('M', bound=pydantic.BaseModel)


class JWSCompactEncoded(StringType):

    @classmethod
    def validate(cls, v: str):
        if not v.count('.') == 2:
            raise ValueError("Invalid JWS Compact Encoding.")
        return cls(v)

    def compact(self):
        return self

    def jose(self, factory: type[M]) -> M:
        protected, payload, signature = str.split(self, '.')
        return factory.model_validate({
            'payload': payload,
            'signatures': [{
                'protected': protected,
                'signature': signature
            }]
        })

    def __repr__(self):
        return f'<{type(self).__name__}>'