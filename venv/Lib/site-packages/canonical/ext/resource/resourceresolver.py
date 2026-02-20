# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal
from typing import TypeVar

from canonical.ext.cache import NullCache
from canonical.lib.protocols import ICache
from .baseresourcerepository import BaseResourceRepository
from .resourceinspector import ResourceInspector
from .resourcekey import ResourceKey


T = TypeVar('T')


class ResourceResolver:
    """Resolve a :class:`~canonical.ext.api.APIResource` instance by a
    supported key type.
    """
    inspector: ResourceInspector = ResourceInspector()

    def __init__(
        self,
        repo: BaseResourceRepository,
        cache: ICache = NullCache()
    ):
        self.cache = cache
        self.repo = repo

    def generate_cache_key(self, model: type[Any], key: ResourceKey) -> str:
        """Return a string that may be used as a cache key based on the
        key of a resource.
        """
        return self.inspector.cache_key(model, key)

    async def from_cache(self, key: str, model: type[T]) -> T | None:
        """Lookup a resource from the cache using the given cache
        key `key`. If there is no cached version of the resource,
        return ``None``.
        """
        return await self.cache.get(key, model)

    async def lookup(
        self,
        key: ResourceKey,
        model: type[T]
    ):
        """Lookup a resource by its key from its master data store."""
        return await self.repo.get(key, model)

    async def resolve(
        self,
        key: ResourceKey,
        model: type[T],
        *,
        ttl: int | None = None,
        mode: Literal['fresh', 'cache-first'] = 'cache-first'
    ) -> T:
        """Resolve a resource by its key using the given `mode`.

        If mode is ``fresh``, force a lookup from the master data
        store of the resource, otherwise attempt to retrieve it
        from the cache first.

        The `ttl` is an integer that specifies the number seconds
        that a freshly retrieved resource should be maintained in
        the cached. If `ttl` is ``None``, then it is up to the
        cache backend to decide on if and how long to cache the
        resource.
        """
        cache_key = self.generate_cache_key(model, key)
        instance = None
        if mode == 'cache-first':
            instance = await self.from_cache(cache_key, model)
        return await self.on_resolved(
            model=model,
            instance=instance or await self.lookup(key, model),
            cache_key=cache_key,
            fresh=instance is None,
            ttl=ttl
        )

    async def on_resolved(
        self,
        model: type[T],
        instance: T,
        *,
        cache_key: str,
        fresh: bool,
        ttl: int | None
    ) -> T:
        if fresh:
            await self.cache.set(cache_key, instance, model, ttl=ttl)
        return instance