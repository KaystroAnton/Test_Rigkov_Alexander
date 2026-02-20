# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Union

import pydantic

from .types import JWECompactEncoded
from .types import JWSCompactEncoded
from .models import JWS
from .protocols import ITokenSignatureVerifier


JOSEType = Union[
    JWS,
    JWECompactEncoded,
    JWSCompactEncoded,
]

class JOSE(pydantic.RootModel[JOSEType]):

    @pydantic.field_validator('root', mode='after')
    def decode_compact(cls, value: Any) -> JWSCompactEncoded | JWECompactEncoded:
        if isinstance(value, JWSCompactEncoded):
            value = value.jose(JWS)
        return value

    @property
    def signatures(self):
        return self._get_signatures()

    @property
    def signature(self):
        return self.signatures[0]

    def compact(self):
        return self.root.compact()

    def is_encoded(self) -> bool:
        return isinstance(self.root, (JWECompactEncoded, JWSCompactEncoded))

    def is_jws(self) -> bool:
        return isinstance(self.root, JWS)

    def model_dump_json(self, **kwargs: Any) -> str:
        kwargs.setdefault('exclude_none', True)
        kwargs.setdefault('exclude_defaults', True)
        kwargs.setdefault('exclude_unset', True)
        return super().model_dump_json(**kwargs)

    def model_post_init(self, _: Any) -> None:
        if isinstance(self.root, JWSCompactEncoded):
            self.root = self.root.jose(JWS)

    @JWS.require
    def verify(self, verifier: ITokenSignatureVerifier):
        assert isinstance(self.root, JWS)
        return self.root.verify(verifier)

    @JWS.require
    def _get_signatures(self):
        assert isinstance(self.root, JWS)
        return self.root.signatures

    def __str__(self):
        return str(self.root)