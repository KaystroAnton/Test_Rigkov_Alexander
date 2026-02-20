# Copyright (C) 2023 Cochise Ruhulessin
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
from typing import Generic
from typing import Literal
from typing import Self
from typing import TypeVar
from typing import TYPE_CHECKING

import pydantic

from canonical.lib.types import SerializableSet
from canonical.utils import deephash
if TYPE_CHECKING:
    from .resource import Resource
from .fields import UID
from .ownerreference import OwnerReference
from .resourcekey import ResourceKey
from .resourcemetadata import ResourceMetadata


N = TypeVar('N')
ObjectMetaType = N


class ObjectMeta(ResourceMetadata, Generic[N]):
    model_config = {'populate_by_name': True}
    allow_on_create = {'name'}
    _version: str = pydantic.PrivateAttr()
    _kind: str = pydantic.PrivateAttr()
    
    created: datetime.datetime | None = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        title="Created",
        description=(
            "`created` is a timestamp representing the server time "
            "when this object was created. It is not guaranteed to be set in "
            "happens-before order across separate operations. Clients may not "
            "set this value. It is represented in RFC3339 form and is in UTC. "
            "Populated by the system. Read-only. Null for lists."
        ),
        frozen=True
    )

    deleted: datetime.datetime | None = pydantic.Field(
        default=None,
        title="Deleted",
        description=(
            "The `deleted` field is an RFC 3339 date and time "
            "at which this resource will be deleted.\n\nThis field "
            "is set by the server when a graceful deletion is "
            "requested by the user, and is not directly settable "
            "by a client.The resource is expected to be deleted "
            "(no longer visible from resource lists, and not "
            "reachable by name) after the time in this field.\n\n"
            "Once set, this value may not be unset or be set "
            "further into the future, although it may be shortened "
            "or the resource may be deleted prior to this time."
        ),
    )

    finalizers: SerializableSet[str] = pydantic.Field(
        default_factory=set,
        description=(
            "Must be empty before the object is deleted from the registry. "
            "Each entry is an identifier for the responsible component that "
            "will remove the entry from the list.\n\nIf the `deleted` field "
            "of the object is non-nil, entries in this list can only be "
            "removed. Finalizers may be processed and removed in any order."
        )
    )

    updated: datetime.datetime | None = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        title="Updated",
        description=(
            "`CreationTimestamp` is a timestamp representing the server time "
            "when this object was updated. Clients may not "
            "set this value. It is represented in RFC3339 form and is in UTC. "
            "Populated by the system. Read-only. Null for lists."
        )
    )

    generation: int = pydantic.Field(
        default=0,
        title="Generation",
        description=(
            "A sequence number representing a specific generation "
            "of the state. Populated by the system. Read-only."
        )
    )

    name: N = pydantic.Field(
        default=...,
        title="Name",
        description=(
            "Name must be unique within a namespace. Is required when creating "
            "resources, although some resources may allow a client to request "
            "the generation of an appropriate name automatically. Name is "
            "primarily intended for creation idempotence and configuration "
            "definition. Cannot be updated."
        ),
        frozen=True
    )

    generate_name: str | None = pydantic.Field(
        default=None,
        alias='generateName',
        description=(
            "An optional prefix, used by the server, to generate a unique name "
            "ONLY IF the `name` field has not been provided. If this field "
            "is used, the name returned to the client will be different than "
            "the name passed. This value will also be combined with a unique "
            "suffix.\n\nThe provided value has the same validation rules as the "
            "`name` field, and may be truncated by the length of the suffix "
            "required to make the value unique on the server.\n\nIf this field "
            "is specified and the generated name exists, the server will "
            "return a 409. Applied only if `name` is not specified."
        ),
        exclude=True
    )

    owner_references: list[OwnerReference] = pydantic.Field(
        default_factory=list,
        alias='ownerReferences',
        description=(
            "List of objects depended by this object. If ALL objects in the "
            "list have been deleted, this object will be garbage collected. "
            "\n\nIf this object is managed by a controller, then an entry in "
            "this list will point to this controller, with the controller "
            "field set to `true`. There cannot be more than one managing "
            "controller."
        )
    )

    resource_version: str = pydantic.Field(
        default='',
        alias='resourceVersion',
        description=(
            "An opaque value that represents the internal version of this object "
            "that can be used by clients to determine when objects have changed. "
            "May be used for optimistic concurrency, change detection, and the "
            "watch operation on a resource or set of resources.\n\nClients must "
            "treat these values as opaque and passed unmodified back to the "
            "server. They may only be valid for a particular resource or set "
            "of resources. Populated by the system. Read-only. Value must be "
            "treated as opaque by clients and ."
        )
    )

    uid: UID = 0

    @property
    def key(self) -> ResourceKey[N]:
        return ResourceKey(api_version=self._api_version, kind=self._kind, name=self.name)

    @classmethod
    def is_namespaced(cls) -> bool:
        return False

    @classmethod
    def add_to_model(cls, model: type[Resource[Any]]) -> None:
        pass

    @classmethod
    def default(cls) -> 'ObjectMeta[Any]':
        raise ValueError("Can not create ObjectMeta without parameters.")

    def attach(self, resource: Resource[Any]):
        self._api_version = resource.api_version
        self._kind = resource.kind

    def get_namespace(self) -> str | None:
        return None

    def in_namespace(self, namespace: str | None) -> bool:
        return namespace is None

    def model_post_init(self, _: Any):
        if len([o for o in self.owner_references if o.controller]) > 1:
            raise ValueError("There can not be more than one controller.")

    def update(self, resource: Any, metadata: Self | None, mode: Literal['replace', 'update']):
        # TODO: metadata should never be None when updating or replacing.
        if metadata is not None:
            self.generation = metadata.generation + 1
            self.uid = metadata.uid
        self.update_resource_version(resource)

    def update_resource_version(self, obj: pydantic.BaseModel):
        data = obj.model_dump(
            mode='json',
            exclude={'api_version', 'kind'}
        )
        self.resource_version = deephash(data, encode='hex')