# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import dataclasses
import datetime
from typing import Any
from typing import Literal

from .base import BaseCache


class MemoryCache(BaseCache):
    __module__: str = 'canonical.ext.cache'
    _global: dict[str, 'CachedObject'] = {}
    objects: dict[str, 'CachedObject']

    @dataclasses.dataclass
    class CachedObject:
        expires: datetime.datetime | None
        value: bytes

        def is_expired(self) -> bool:
            now = datetime.datetime.now(datetime.timezone.utc)
            return self.expires is not None and (self.expires < now)

    def __init__(self, scope: Literal['global', 'local'], *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.scope = scope
        self.objects = {}
        if scope == 'global':
            self.objects = MemoryCache._global

    async def fetch(self, key: str, *args: Any, **kwargs: Any) -> bytes | None:
        value = None
        obj = self.objects.get(key)
        if obj is not None and not obj.is_expired():
            value = obj.value
        return value

    async def put(
        self,
        key: str,
        value: bytes,
        *_: Any,
        ttl: int | None = None,
        **__: Any
    ) -> None:
        now = datetime.datetime.now(datetime.timezone.utc)
        expires = None
        if ttl:
            expires = now + datetime.timedelta(seconds=ttl)
        self.objects[key] = self.CachedObject(expires, value)