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
from typing import cast
from typing import Annotated
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import Self
from typing import TypeVar

import pydantic

from canonical.lib.types import SerializableSet
from canonical.lib.utils import deephash
from .apimodel import APIModel
from .apimodelfield import APIModelField
from .meta import APIVersionedMeta
from .ownerreference import OwnerReference
from .uidreference import UIDReference


N = TypeVar('N', bound=str)


class ObjectMeta(APIModel, Generic[N], group='core', version='v1'):
    model_config = {'populate_by_name': True}
    server_fields: ClassVar[set[str]] = {
        'created',
        'deleted',
        'finalizers',
        'generation',
        'resource_version',
        'owner_references',
        'updated',
        'uid'
    }

    annotations: Annotated[dict[str, Any], APIModelField(
        default_factory=dict,
        title="Annotations",
        description=(
            "Annotations is an unstructured key value map stored with "
            "a resource that may be set by external tools to store "
            "and retrieve arbitrary metadata. They are not queryable and "
            "should be preserved when modifying objects."
        ),
        when={'create', 'update', 'store', 'view'}
    )]

    labels: Annotated[dict[str, str | None], APIModelField(
        default_factory=dict,
        title="Labels",
        description=(
            "Map of string keys and values that can be used to organize and "
            "categorize (scope and select) objects."
        ),
        when={'create', 'update', 'store', 'view'}
    )]

    tags: Annotated[SerializableSet[str], APIModelField(
        default_factory=set,
        description=(
            "An array of tags that may be used to classify an object "
            "if a label or annotation is not applicable."
        ),
        when={'create', 'update', 'store', 'view'}
    )]

    created: Annotated[datetime.datetime | None, APIModelField(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        title="Created",
        description=(
            "`created` is a timestamp representing the server time "
            "when this object was created. It is not guaranteed to be set in "
            "happens-before order across separate operations. Clients may not "
            "set this value. It is represented in RFC3339 form and is in UTC. "
            "Populated by the system. Read-only. Null for lists."
        ),
        frozen=True,
        when={'store', 'view'}
    )]

    deleted: Annotated[datetime.datetime | None, APIModelField(
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
        when={'store', 'view'}
    )]

    finalizers: Annotated[SerializableSet[str], APIModelField(
        default_factory=set,
        description=(
            "Must be empty before the object is deleted from the registry. "
            "Each entry is an identifier for the responsible component that "
            "will remove the entry from the list.\n\nIf the `deleted` field "
            "of the object is non-nil, entries in this list can only be "
            "removed. Finalizers may be processed and removed in any order."
        ),
        when={'store', 'view'}
    )]

    generation: Annotated[int, APIModelField(
        default=0,
        title="Generation",
        description=(
            "A sequence number representing a specific generation "
            "of the state. Populated by the system. Read-only."
        ),
        frozen=True,
        when={'store', 'view'}
    )]

    name: Annotated[N, APIModelField(
        default=...,
        title="Name",
        description=(
            "Name must be unique within a namespace. Is required when creating "
            "resources, although some resources may allow a client to request "
            "the generation of an appropriate name automatically. Name is "
            "primarily intended for creation idempotence and configuration "
            "definition. Cannot be updated."
        ),
        frozen=True,
        when={'create', 'store', 'view'}
    )]

    owner_references: Annotated[list[OwnerReference], APIModelField(
        default_factory=list,
        alias='ownerReferences',
        description=(
            "List of objects depended by this object. If ALL objects in the "
            "list have been deleted, this object will be garbage collected. "
            "\n\nIf this object is managed by a controller, then an entry in "
            "this list will point to this controller, with the controller "
            "field set to `true`. There cannot be more than one managing "
            "controller."
        ),
        frozen=True,
        when={'store', 'view'}
    )]

    resource_version: Annotated[str, APIModelField(
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
        ),
        when={'store', 'view'}
    )]

    uid: Annotated[int, APIModelField(
        default=...,
        when={'store', 'view'},
        frozen=True
    )]

    updated: datetime.datetime = APIModelField(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        title="Updated",
        description=(
            "`CreationTimestamp` is a timestamp representing the server time "
            "when this object was updated. Clients may not "
            "set this value. It is represented in RFC3339 form and is in UTC. "
            "Populated by the system. Read-only. Null for lists."
        ),
        frozen=True,
        when={'store', 'view'}
    )

    @classmethod
    def with_namespace(cls) -> type[Self]:
        args = cls.__pydantic_generic_metadata__.get('args')
        if not args:
            raise TypeError(
                "Can only create namespaced implementations of ObjectMeta "
                "from concrete classes."
            )
        t = type(
            f'Namespaced{cls.__name__}',
            (cls,),
            {
                '__annotations__': {
                    'name': cls.model_fields['name'].annotation,
                    'namespace': str
                },
                '__builder__': None,
                '__create_model__': None,
                '__mode__': 'domain',
                '__parameters__': args,
                'model_config': cls.model_config,
            },
        )
        return cast(type[Self], t)

    @pydantic.model_validator(mode='before') # type: ignore
    def preprocess(cls, values: dict[str, Any] | Self):
        if isinstance(values, dict):
            now = created = datetime.datetime.now(datetime.timezone.utc)
            if 'created' in cls.model_fields:
                created = values.setdefault('created', now)
            if 'updated' in cls.model_fields:
                values.setdefault('updated', created)
        return values

    @pydantic.field_serializer('resource_version', when_used='always', check_fields=False)
    def serialize_resource_name(self, value: str, _: Any) -> str:
        assert self.parent is not None
        return deephash(
            obj={
                **self.parent.model_dump(exclude={'metadata'}, mode='json'),
                'metadata': self.model_dump(exclude={'resource_version'}, mode='json')
            },
            encode='hex'
        )

    @property
    def key(self) -> UIDReference:
        if self.parent is None:
            raise TypeError(
                f"{type(self).__name__} is not attached to any known "
                "instance"
            )
        return UIDReference(
            api_version='v1', # type: ignore
            kind='ObjectDescriptor',
            uid=self.uid,
        )

    def cache_key(self, meta: APIVersionedMeta[Any]):
        return meta.cache_key(self.name, getattr(self, 'namespace', None))

    def dao(self):
        if self.parent is None:
            raise TypeError(
                f"{type(self).__name__} is not attached to any known "
                "instance"
            )
        assert self.parent is not None
        obj = self.__stored_model__.model_validate({
            **self.model_dump(),
            **self.parent.model_dump(include={'api_version', 'kind'}),
        })
        obj.add_to_parent(self.parent)
        return obj

    def get_controller(self) -> OwnerReference | None:
        """Return a :class:`OwnerReference` pointing to the
        controller, or ``None``.
        """
        ctrl: list[OwnerReference | None] = [
            o for o in self.owner_references if o.controller
        ]
        if len(ctrl) > 1:
            raise ValueError("Object has multiple controllers")
        ctrl.append(None)
        return ctrl.pop(0)

    def get_namespace(self):
        return getattr(self, 'namespace', None)

    def in_namespace(self, namespace: str):
        return getattr(self, 'namespace', None) == namespace