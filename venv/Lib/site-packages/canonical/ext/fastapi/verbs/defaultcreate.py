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
from .create import Create
from ..params import ResourceRepository


T = TypeVar('T', bound=APIResourceType)


class DefaultCreate(Create[T]):
    creates = True
    detail = False
    exists = False
    method = 'POST'
    requires_body = True
    status_code = 201
    verb = 'create'

    async def handle(
        self,
        repo: ResourceRepository,
        obj: APIResourceType
    ) -> APIResourceType:
        obj = await repo.persist(
            model=self.model,
            new=self.model.model_validate({
                'metadata': {
                    **obj.metadata.model_dump(),
                    'generation': 1,
                    'uid': await repo.allocate(self.model)
                },
                **obj.model_dump(exclude={'metadata'})
            })
        )
        self.logger.debug(
            "Persisted object (kind: %s, uid: %s).",
            obj.kind, obj.metadata.uid
        )
        return obj