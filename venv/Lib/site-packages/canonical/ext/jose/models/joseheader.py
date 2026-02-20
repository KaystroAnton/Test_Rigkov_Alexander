# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import json
from typing import Any
from typing import Generic
from typing import TypeVar

import pydantic

from canonical.lib.utils.encoding import b64encode
from .jsonwebkey import JSONWebKey


A = TypeVar('A')


class JOSEHeader(pydantic.BaseModel, Generic[A]):
    alg: A
    cty: str | None = None
    crit: list[str] = []
    jku: str | None = None
    jwk: JSONWebKey | None = None
    kid: str | None = None
    typ: str | None = None
    x5c: str | None = None
    x5t: str | None = None
    x5t_sha256: str | None = pydantic.Field(default=None, alias='x5t#S256')
    x5u: str | None = None
    claims: dict[str, Any] = {}

    @pydantic.model_validator(mode='before') # type: ignore
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        return {
            **{
                name: values[name] for name in cls.model_fields.keys()
                if name in values and name != 'claims'
            },
            **(values.get('claims') or {})
        }

    def encode(self, **kwargs: Any) -> bytes:
        kwargs.setdefault('exclude_none', True)
        kwargs.setdefault('exclude_defaults', True)
        kwargs.setdefault('exclude_unset', True)
        exclude = kwargs.setdefault('exclude', set())
        exclude.add('claims')
        claims = self.model_dump(**kwargs)
        claims.update(self.claims)
        return b64encode(json.dumps(claims))

    def __bytes__(self):
        return self.encode()