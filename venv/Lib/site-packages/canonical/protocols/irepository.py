# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Generic
from typing import Protocol
from typing import TypeVar

from canonical.exceptions import DoesNotExist
from canonical.exceptions import MultipleObjectsReturned


I = TypeVar('I')


class IRepository(Protocol, Generic[I]):
    __module__: str = 'canonical.protocols'
    InstanceType = I
    DoesNotExist: type[LookupError] = DoesNotExist
    MultipleObjectsReturned: type[LookupError] = MultipleObjectsReturned

    async def delete(self, obj: I | int | str) -> None:
        ...

    async def get(self, pk: Any) -> I | None:
        ...

    async def one(self, pk: Any) -> I:
        ...

    async def persist(self, obj: I) -> None:
        ...