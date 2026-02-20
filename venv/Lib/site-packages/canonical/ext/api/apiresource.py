# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
from typing import cast
from typing import overload
from typing import Any
from typing import Annotated
from typing import Generic
from typing import Literal
from typing import Self
from typing import TypeVar

from canonical.ext.api.protocols import IObjectIdentifier
from .apimodelfield import APIModelField
from .apiversioned import APIVersioned
from .bases import BaseResource
from .builders import APIResourceClassBuilder
from .objectmeta import ObjectMeta
from .objectreference import ObjectReference
from .apiversionedmeta import APIVersionedMeta

K = TypeVar('K', bound=str)
M = TypeVar('M')


class APIResource(APIVersioned, BaseResource, Generic[K], abstract=True):
    __abstract__ = True
    __builder_class__ = APIResourceClassBuilder

    metadata: Annotated[
        ObjectMeta[K],
            APIModelField(
            title='Metadata',
            description=(
                "`ObjectMeta` is metadata that all persisted resources "
                "must have, which includes all objects users must create."
            ),
            when={'create', 'store', 'update', 'view'}
        )
    ]

    @property
    def cache_key(self):
        return self.metadata.cache_key(self.__meta__)

    @property
    def key(self) -> IObjectIdentifier[Self]:
        return self.get_object_ref(self.__meta__)\
            .with_model(self.model)

    @property
    def model(self):
        return type(self)

    @property
    def name(self) -> K:
        return self.metadata.name

    @overload
    def get_controller(self, require: Literal[True], model: type[M]) -> IObjectIdentifier[M]:
        ...

    @overload
    def get_controller(self, require: Literal[False], model: type[M]) -> IObjectIdentifier[M] | None:
        ...

    def get_controller(self, require: bool, model: type[M]) -> IObjectIdentifier[M] | None:
        ctrl = self.metadata.get_controller()
        if require and not ctrl:
            raise ValueError(
                f"{self.model.__name__} object is expected to have a "
                f"controller, but has none (name: {self.metadata.name}, "
                f"namespace: {self.get_namespace()})."
            )
        if ctrl:
            ctrl.with_model(model)
        return cast(IObjectIdentifier[M], ctrl)

    @overload
    def get_namespace(self, require: Literal[False] = False) -> str | None: ...

    @overload
    def get_namespace(self, require: Literal[True]) -> str: ...

    def get_namespace(self, require: bool = False) -> str | None:
        ns = self.metadata.get_namespace()
        if require and not ns:
            raise TypeError("Object is not namespaced.")
        return ns

    def get_object_ref(self, meta: APIVersionedMeta[Any]) -> ObjectReference:
        ref = ObjectReference(
            api_version=meta.api_version,
            kind=meta.kind,
            name=str(self.name)
        )
        ref.attach(self.metadata)
        return ref

    def in_namespace(self, namespace: str):
        return self.metadata.in_namespace(namespace)

    def replacable(self) -> bool:
        return True

    def update(self, old: Self | None) -> tuple[Self, bool]:
        """Return a tuple containing an instance with updated
        metadata and a boolean indicating if there are any
        changed that need to be persisted.
        """
        if old is None:
            return self, True
        generation = self.metadata.generation
        os = old.model_dump(exclude={'api_version', 'kind', 'metadata', 'status'})
        ns = self.model_dump(exclude={'api_version', 'kind', 'metadata', 'status'})
        if os != ns:
            generation += 1
        data = {
            **self.model_dump(exclude={'metadata'}),
            'metadata': {
                **self.metadata.model_dump(exclude={'generation', 'updated'}),
                'generation': generation,
                'updated': datetime.datetime.now(datetime.timezone.utc),
            }
        }
        return self.model_validate(data), True