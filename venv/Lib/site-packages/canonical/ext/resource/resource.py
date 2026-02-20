# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
import datetime
import inspect
import logging
from typing import cast
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import Literal
from typing import Self
from typing import TypeVar
from typing import TYPE_CHECKING

import pydantic
import yaml

from canonical.exceptions import Immutable
from canonical.exceptions import Inconsistent
from canonical.exceptions import Stale
from canonical.ext.api import ObjectReference
from canonical.protocols import IStorage
from canonical.protocols import ITransaction
from canonical.utils import deephash
from .apiresourcelist import APIResourceList
from .listbase import ListBase
from .namespacedobjectmeta import NamespacedObjectMeta
from .objectmeta import ObjectMeta
from .resourcekey import ResourceKey
from .resourcemeta import ResourceMeta
from .transientmeta import TransientMeta
if TYPE_CHECKING:
    from .baseresourcerepository import BaseResourceRepository
    from .rootresource import RootResource

__all__: list[str] = [
    'Resource'
]

M = ObjectMetaType = TypeVar('M', bound=ObjectMeta[Any] | TransientMeta)
S = TypeVar('S', bound='Resource[Any]')
V = TypeVar('V')
NOT_PROVIDED: object = object()


class Resource(pydantic.BaseModel, Generic[M]):
    _storage: BaseResourceRepository | None = pydantic.PrivateAttr(default=None)
    List: ClassVar[type[ListBase[Any, Any]]]
    metadata_class: ClassVar[type[ObjectMeta[Any] | TransientMeta]]
    model_config = {'populate_by_name': True}
    base_path: ClassVar[str]
    group: ClassVar[str]
    logger: ClassVar[logging.Logger] = logging.getLogger('canonical.ext.resource')
    plural: ClassVar[str]
    InputModel: ClassVar[type[Self]]
    __meta__: ClassVar[ResourceMeta]

    api_version: str = pydantic.Field(
        default=...,
        alias='apiVersion',
        title="API Version",
        description=(
            "The `apiVersion` field defines the versioned schema of this "
            "representation of an object. Servers should convert recognized "
            "schemas to the latest internal value, and may reject "
            "unrecognized values."
        ),
        frozen=True
    )

    kind: str = pydantic.Field(
        default=...,
        description=(
            "Kind is a string value representing the REST resource this "
            "object represents. Servers may infer this from the endpoint "
            "the client submits requests to. Cannot be updated. In `CamelCase`."
        ),
        frozen=True
    )

    metadata: M = pydantic.Field(
        default=...,
        title='Metadata',
        description=(
            "`ObjectMeta` is metadata that all persisted resources "
            "must have, which includes all objects users must create."
        )
    )

    @property
    def scoped(self):
        n = self.metadata.name
        if self.is_namespaced():
            assert isinstance(self.metadata, NamespacedObjectMeta)
            n = f'{self.metadata.namespace}/{self.metadata.name}'
        return n

    @classmethod
    def is_namespaced(cls) -> bool:
        metadata_cls = cls.model_fields['metadata'].annotation
        if not inspect.isclass(metadata_cls):
             return False
        assert metadata_cls in {ObjectMeta, NamespacedObjectMeta, TransientMeta}\
            or issubclass(metadata_cls, (ObjectMeta, NamespacedObjectMeta, TransientMeta))
        return metadata_cls.is_namespaced() # type: ignore

    @classmethod
    def is_destroyable(cls) -> bool:
        """Return a boolean indicating if the resource may be destroyed
        by a client.
        """
        return True

    @classmethod
    def is_purgable(cls) -> bool:
        """Return a boolean indicating if the resources may be purged
        by a client.
        """
        return True

    @classmethod
    def new(cls, name: Any, **params: Any):
        return cls.model_validate({
            **params,
            'metadata': {
                'name': name
            }
        })

    @property
    def key(self):
        assert not isinstance(self.metadata, TransientMeta)
        ref = ObjectReference(
            api_version=self.api_version,
            kind=self.kind,
            name=self.metadata.name,
            namespace=self.metadata.get_namespace() or '',
            resource_version=self.metadata.resource_version or '',
            uid=self.metadata.uid
        )
        return ref.attach(self.metadata).with_model(type(self))

    @property
    def relname(self) -> str:
        return f'{self.plural}/{self.metadata.name}'

    @classmethod
    def add_to_root(cls, root: type[RootResource[Any]], meta: ResourceMeta) -> None:
        assert cls.model_fields['metadata'].annotation
        cls.model_fields['api_version'].default = meta.api_version
        cls.model_fields['api_version'].annotation = Literal[f'{meta.api_version}']
        cls.model_fields['kind'].default = root.__name__
        cls.model_fields['kind'].annotation = Literal[f'{root.__name__}']
        assert cls.model_rebuild(force=True)
        if not hasattr(cls, 'InputModel'):
            # TODO: This will cause weird results if a subclass of Resource
            # is added to multiple RootResource subclasses.
            cls.InputModel = ResourceMeta.build_input_model(
                model=cls,
                meta=cls.model_fields['metadata'].annotation,
                fields=cls.model_fields
            )

    @classmethod
    def has_state(cls) -> bool:
        return False

    @classmethod
    def model_validate_input(cls, data: dict[str, Any]) -> Self:
        return cls.model_validate(data)

    @classmethod
    def setup_meta(cls, version: str, contribute: bool = True):
        meta = ResourceMeta.fromqualname(cls, version)
        if contribute:
            meta.contribute_to_class(cls, cls.model_fields)
        return meta

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__()

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__()
        qualname = kwargs.get('version')
        if qualname:
            cls.setup_meta(qualname)

            # Create the list type.
            cls.List = type(f'{cls.__name__}List', (ListBase[Literal[f'{cls.__name__}List'], cls],), { # type: ignore
                'items': pydantic.Field(
                    default_factory=list,
                    description=(
                        "The `items` member contains an array "
                        f"of `{cls.__name__}` objects."
                    )
                ),
                '__annotations__': {'items': list[cls]}
            })
            cls.List.model_fields['kind'].default = f'{cls.__name__}List'
            cls.List.model_rebuild()

            metadata_class = cls.model_fields['metadata'].annotation
            if not inspect.isclass(metadata_class):
                return None
            assert metadata_class in {ObjectMeta, NamespacedObjectMeta, TransientMeta}\
                or issubclass(metadata_class, (ObjectMeta, NamespacedObjectMeta, TransientMeta))
            cls.metadata_class = metadata_class
            cls.model_fields['metadata'].default_factory = metadata_class.default # type: ignore
            #cls.model_rebuild()

    def can_change(self, old: Self) -> bool:
        return True

    def get_comparison_fields(self) -> set[str]:
        return {'spec'}

    def get_mutable_data(self) -> dict[str, Any]:
        return self.model_dump(
            mode='json',
            include=self.get_mutable_fields()
        )

    def get_mutable_fields(self) -> set[str]:
        return set()

    def get_namespace(self) -> str | None:
        return self.metadata.get_namespace()

    def in_namespace(self, namespace: str | None) -> bool:
        return self.metadata.in_namespace(namespace)

    def is_changed(self, old: Self) -> bool:
        a = deephash(self.model_dump(mode='json', include=self.get_comparison_fields()))
        b = deephash(old.model_dump(mode='json', include=old.get_comparison_fields()))
        return a != b

    def is_created(self):
        return bool(self.metadata.resource_version)

    def is_consistent(self) -> bool:
        return True

    def is_persistable(self) -> bool:
        return isinstance(self.metadata, (ObjectMeta, NamespacedObjectMeta))

    def model_post_init(self, _: Any) -> None:
        self.metadata.attach(self)

    def model_dump_yaml(self, indent: int =2, **kwargs: Any) -> str:
        return yaml.safe_dump(  # type: ignore
            self.model_dump(mode='json', by_alias=True, **kwargs),
            default_flow_style=False
        )

    async def persist(
        self,
        storage: Any | None = None,
        mode: Literal['create', 'replace'] = 'create',
        transaction: ITransaction | None = None
    ) -> Self:
        return await self.persist_key(self.key, storage, mode, transaction)

    async def persist_key(
        self,
        key: ResourceKey,
        storage: BaseResourceRepository | None = None,
        mode: Literal['create', 'replace', 'update'] = 'create',
        transaction: ITransaction | None = None,
        transfer: bool = False
    ) -> Self:
        assert isinstance(self.metadata, (ObjectMeta, NamespacedObjectMeta))
        if not self.is_consistent():
            raise Inconsistent(
                f"The {type(self).__name__} is in an inconsistent state."
            )
        storage = storage or self._storage
        if storage is None:
            raise TypeError(
                f'{type(self).__name__} is not attached to any storage '
                'and the `storage` parameter is None.'
            )
        try:
            old = await storage.get(key, type(self))
            old.metadata.updated = datetime.datetime.now(datetime.timezone.utc)
            assert old is not None
        except storage.DoesNotExist:
            if mode != 'create':
                raise
            old = None

            # We are creating a new object here, so the generation
            # should be bumped to the first version.
            self.metadata.generation = 1

            # Clear any existing values for updated, uid
            self.metadata.updated = self.metadata.created
            self.metadata.uid = await storage.allocate(key.get_model())

            # The deleted field can not be set on new objects,
            # because there is nothing to delete.
            if self.metadata.deleted: # type: ignore
                raise Immutable(
                    "The .metadata.deleted field must not be set on new "
                    f"{type(self).__name__} objects."
                )
        if mode == 'create' and old is not None:
            raise storage.Duplicate
        if old is not None and mode == 'update':
            nm = cast(ObjectMeta[Any], self.metadata)
            om = cast(ObjectMeta[Any], old.metadata)
            assert isinstance(old.metadata, (ObjectMeta, NamespacedObjectMeta))

            # If the generation is non-zero, then the generation of the persisted
            # object MUST match it.
            if nm.generation and (nm.generation != om.generation):
                raise Stale

            # Same applies to the resource version.
            if nm.resource_version and (nm.resource_version != om.resource_version):
                raise Stale

            # This should never happen, but its fine to check anyway.
            if (getattr(nm, 'namespace', None) != getattr(om, 'namespace', None))\
            and not transfer:
                raise Immutable(
                    "The namespace of an object can not be changed."
                )

            # If the existing state does not allow transition to the
            # new state, throw an immutable exception.
            if not self.can_change(old):
                raise Immutable(
                    f"{type(self).__name__} does not allow the specified "
                    "changes."
                )

            # Merge the metadata of the new instance into the old instance.
            self.metadata = om.merge(nm) # type: ignore

            # Bump the generation (TODO: only bump if there are actual)
            # changes.
            if self.is_changed(old):
                self.metadata.generation += 1

        if old is not None and mode == 'replace':
            assert self.replacable()
            self.metadata.update(self, cast(Any, old.metadata), mode=mode)
            # TODO: on stateful resources, clear the status.
            self._on_replaced(old)

        # Resource version must be updated on every write.
        self.metadata.update_resource_version(self)
        return await storage.persist(self, transaction=transaction, model=key.get_model())

    def replacable(self) -> bool:
        return True

    def _on_replaced(self, old: Self):
        pass