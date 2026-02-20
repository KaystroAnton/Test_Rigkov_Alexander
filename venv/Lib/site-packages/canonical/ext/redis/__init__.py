# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal

from redis import asyncio as aioredis

from canonical.ext.cache import BaseCache


class RedisCache(BaseCache):
    __module__: str = 'canonical.ext.redis'

    def __init__(
        self,
        url: str,
        keyalg: Literal['sha256'] | None = None,
        prefix: str | None = None,
        **kwargs: Any
    ):
        super().__init__(keyalg, prefix, **kwargs)
        self.client: aioredis.Redis = aioredis.from_url(url) # type: ignore

    async def fetch(self, key: str) -> bytes | None:
        return await self.client.get(key) # type: ignore

    async def put(
        self,
        key: str,
        value: Any,
        encrypt: bool = False,
        ttl: int | None = None
    ) -> None:
        await self.client.set(key, value, ex=ttl) # type: ignore
