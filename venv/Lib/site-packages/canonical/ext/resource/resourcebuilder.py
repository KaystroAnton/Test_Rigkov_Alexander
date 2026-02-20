# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
from typing import Any
from typing import Generic
from typing import NotRequired
from typing import TypeVar
from typing import TypedDict

from canonical.lib.protocols import IBuilder
from .objectmeta import ObjectMeta
from .ownerreference import OwnerReference
from .rootresource import ResourceType


T = TypeVar('T')


class APIResourceBuilder(IBuilder[T], Generic[T]):
    block_owner_deletion: bool = True
    metadata: 'ObjectMetadataDict'
    needs_controller: bool = True

    class ObjectMetadataDict(TypedDict):
        annotations: dict[str, str]
        created: datetime.datetime
        labels: dict[str, str]
        namespace: NotRequired[str]
        owner_references: list[OwnerReference]
        tags: list[str]
        updated: datetime.datetime

    def __init__(self, initial: dict[str, Any] | None = None):
        self.now = datetime.datetime.now(datetime.timezone.utc)
        self.metadata = {
            'annotations': {},
            'created': self.now,
            'labels': {},
            'owner_references': [],
            'tags': [],
            'updated': self.now,
        }
        self.spec = initial or {}

    def annotate(self, name: str, value: str):
        self.metadata['labels'][name] = value

    def annotations(self, annotations: dict[str, str]):
        self.metadata['annotations'].update(annotations)

    def has_controller(self) -> bool:
        return any([x.controller for x in self.metadata['owner_references']])

    def label(self, name: str, value: str):
        self.metadata['labels'][name] = value

    def labels(self, labels: dict[str, str]):
        self.metadata['labels'].update(labels)

    def own(self, owner: ResourceType, controller: bool = False):
        assert owner.metadata.uid
        if controller and owner.is_namespaced():
            ns = self.metadata.get('namespace')
            if ns and ns != owner.metadata.namespace:
                raise ValueError(
                    f"Owner must be in the same namespace (namespace={ns})."
                )
            self.metadata['namespace'] = owner.metadata.namespace
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

    async def build(self) -> T:
        raise NotImplementedError