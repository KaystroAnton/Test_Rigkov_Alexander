# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
import datetime
from typing import Any
from typing import TypeVar
from typing import TYPE_CHECKING

import pydantic

from canonical.ext.builder import BaseBuilder
from .resourcerepository import BaseResourceRepository
if TYPE_CHECKING:
    from .. import APIResourceType


T = TypeVar('T', bound=pydantic.BaseModel)


class BaseResourceBuilder(BaseBuilder[T]):
    model: type[T]
    metadata: dict[str, Any]
    block_owner_deletion: bool = True

    def __init__(
        self,
        repo: BaseResourceRepository,
        initial: dict[str, Any] | None = None
    ):
        super().__init__()
        self.now = datetime.datetime.now(datetime.timezone.utc)
        self.metadata = {
            'annotations': {},
            'created': self.now,
            'updated': self.now,
            'labels': {},
            'owner_references': [],
            'uid': None
        }
        self.repo = repo
        self.spec = initial or {}

    def annotate(self, name: str, value: str):
        self.metadata['annotations'][name] = value

    def get_model_input(self) -> dict[str, Any]:
        return {
            'metadata': self.metadata,
            'spec': self.spec
        }

    def has_controller(self) -> bool:
        return any([x.controller for x in self.metadata['owner_references']])

    def label(self, name: str, value: str):
        self.metadata['labels'][name] = value

    def own(self, owner: APIResourceType, controller: bool = False):
        from ..ownerreference import OwnerReference # TODO
        assert owner.metadata.uid
        meta = owner.__meta__
        if controller and meta.is_namespaced():
            self.metadata['namespace'] = owner.get_namespace()
        self.metadata['owner_references'].append(
            OwnerReference.model_validate({
                'api_version': owner.api_version,
                'kind': owner.kind,
                'uid': owner.metadata.uid,
                'name': owner.metadata.name,
                'controller': controller,
                'block_owner_deletion': self.block_owner_deletion
            })
        )

    async def prepare(self):
        pass

    async def build(self) -> T:
        return self.model.model_validate(self.get_model_input())

    async def _build(self):
        self.metadata['uid'] = await self.repo.allocate(self.model)
        await self.prepare()
        return await self.build()

    def __await__(self):
        return self._build().__await__()