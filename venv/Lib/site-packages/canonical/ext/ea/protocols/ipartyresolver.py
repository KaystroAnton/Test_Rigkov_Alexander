# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging
from typing import Any
from typing import Callable
from typing import Generic
from typing import Protocol
from typing import TypeVar

import pydantic

from ..transactionparty import BaseTransactionParty


D = TypeVar('D', covariant=True, bound=pydantic.BaseModel)
G = TypeVar('G')
P = TypeVar('P')
R = TypeVar('R')
T = TypeVar('T', bound=BaseTransactionParty[Any, Any], contravariant=True)


class IPartyResolver(Protocol, Generic[P, R, D, T]):
    logger: logging.Logger = logging.getLogger('canonical.ext.ea')

    def descriptor(
        self,
        party: P,
        role: R,
        require: set[str],
        *,
        optional: set[str],
        **kwargs: Any
    ) -> D:
        ...

    def on_created(self, party: P, ref: T) -> None:
        pass

    def on_role_assigned(self, party: P, role: R) -> None:
        pass

    async def assign_role(self, party: P, role_name: str) -> tuple[R, bool]:
        ...

    async def factory(self, ref: T) -> P:
        ...

    async def get(self, ref: T) -> P | None:
        ...

    async def persist_party(self, instance: P) -> None:
        ...

    async def persist_role(self, instance: R) -> None:
        ...

    async def resolve(
        self,
        party: P,
        txp: T,
        name: str,
        *,
        role: R | None,
        required: bool = True,
        force: bool = False
    ):
        ...

    async def resolve_references(
        self,
        party: P,
        ref: T,
        role: R,
        require: set[str],
        optional: set[str],
        force: bool = False
    ) -> None:
        for name in {*require, *optional}:
            await self.resolve(party, ref, name, role=role, required=name not in optional, force=force)

    async def create(self, ref: T, require: set[str], optional: set[str]) -> P:
        party = await self.factory(ref)
        self.on_created(party, ref)
        await self.persist_party(party)
        return party

    async def transaction(
        self,
        ref: T,
        require: set[str] | None = None,
        optional: set[str] | None = None,
        factory: Callable[[dict[str, Any]], Any] | None = None,
        force: bool = False
    ) -> D:
        require = require or set()
        optional = optional or set()
        party = await self.get(ref)
        if party is None:
            party = await self.create(ref, require, optional)
        role, assigned = await self.assign_role(party, ref.role)
        if assigned:
            self.logger.info(
                "Assigned role to party (party: %s, role: %s)",
                str(party), str(role)
            )
            self.on_role_assigned(party, role)
        await self.resolve_references(party, ref, role, require, optional, force=force)
        descriptor = self.descriptor(party, role, require,
            optional=optional, display_name=ref.display_name)
        if factory:
            descriptor = factory(descriptor.model_dump())
        return descriptor