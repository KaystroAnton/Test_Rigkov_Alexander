# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Generic
from typing import TypeVar

import pydantic

from canonical.lib.types import UnixTimestamp

A = TypeVar('A')
K = TypeVar('K')
O = TypeVar('O')
U = TypeVar('U')


class BaseJWK(pydantic.BaseModel, Generic[K, A, O, U]):
    alg: A | None = None
    crv: str | None = None
    exp: UnixTimestamp | None = None
    iat: UnixTimestamp | None = None
    key_ops: list[O] | None = None
    kid: str | None = None
    kty: K
    nbf: UnixTimestamp | None = None
    use: U | None = None

    @property
    def thumbprint(self) -> str:
        raise NotImplementedError

    def verify(
        self,
        signature: bytes,
        payload: bytes,
        *,
        alg: str | None = None
    ) -> bool:
        raise NotImplementedError