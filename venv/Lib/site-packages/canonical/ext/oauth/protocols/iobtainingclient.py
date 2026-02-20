# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
from typing import Any
from typing import Generic
from typing import Protocol
from typing import TypeVar

import httpx

from canonical.ext.oauth.types import Error
from canonical.ext.oauth.types import ProtocolViolation


R = TypeVar('R', covariant=True)


class IObtainingClient(Protocol, Generic[R]):

    @property
    def id(self) -> str:
        ...

    def configure(self, **kwargs: Any) -> IObtainingClient[R]:
        """Configure a new instance with the given parameters."""
        ...

    async def obtain(
        self,
        grant: Any,
        http: httpx.AsyncClient | None = None
    ) -> R | Error | ProtocolViolation:
        ...