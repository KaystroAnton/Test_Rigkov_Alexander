import contextlib
from typing import Any
from typing import TypeVar

import pydantic
from canonical.protocols import IRepository


T = TypeVar('T', bound='PersistedModel')


class PersistedModel(pydantic.BaseModel):
    _repo: IRepository[Any] = pydantic.PrivateAttr()

    def attach(self: T, storage: IRepository[T]):
        self._repo = storage
        return self

    @contextlib.asynccontextmanager
    async def atomic(self):
        try:
            yield
            await self.persist()
        except Exception:
            raise

    @contextlib.asynccontextmanager
    async def consume(self):
        try:
            yield
            await self.delete()
        except Exception:
            raise

    async def delete(self) -> None:
        await self._repo.delete(self)

    async def persist(self) -> None:
        await self._repo.persist(self)