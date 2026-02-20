# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import TypeVar

from canonical.ext.api import APIResourceType
from .replace import Replace
from ..params import ResourceRepository
from ..params import RequestResource


T = TypeVar('T', bound=APIResourceType)


class DefaultReplace(Replace[T]):
    creates = False
    detail = True
    exists = True
    method = 'PUT'
    requires_body = True
    status_code = 205
    verb = 'replace'

    async def handle(
        self,
        repo: ResourceRepository,
        old: RequestResource,
        new: APIResourceType
    ) -> APIResourceType:
        return await self.replace(repo, old, new)

    async def replace(
        self,
        repo: ResourceRepository,
        old: RequestResource,
        new: APIResourceType
    ) -> APIResourceType:
        assert old is not None
        old.replace(new)
        await repo.persist(self.model, old)
        return old