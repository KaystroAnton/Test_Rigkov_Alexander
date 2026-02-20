# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
import dataclasses
from typing import get_args
from typing import Any
from typing import TypeVar
from typing import TYPE_CHECKING

import pydantic

from .bases.reference import BaseReference
from .bases.resource import BaseResource
if TYPE_CHECKING:
    from .apimodel import APIModel
    from .apiversioned import APIVersioned
    from .meta import APIVersionedMeta


A = TypeVar('A', bound='APIModel')
T = TypeVar('T', bound=Any)


class APIModelInspector:

    @dataclasses.dataclass
    class ModelStateTuple:
        domain: type[BaseResource]
        create: type[pydantic.BaseModel] | None
        update: type[pydantic.BaseModel] | None
        stored: type[pydantic.BaseModel] | None
        output: type[pydantic.BaseModel] | None

    def cache_key(self, model: type[APIVersioned[Any]], name: str, namespace: str | None = None) -> str:
        """Return a string identifying a single resource to be
        used as a cache key.
        """
        return model.__meta__.cache_key(name, namespace)

    def get_field_annotations(self, model: type[pydantic.BaseModel]):
        return {name: field.annotation for name, field in model.model_fields.items()}

    def get_models(self, model: type[BaseResource]) -> ModelStateTuple:
        return self.ModelStateTuple(
            model,
            getattr(model, '__create_model__', None),
            None, None, None
            #model.__update_model__,
            #model.__stored_model__,
            #model.__output_model__,
        )

    def get_reference_tree(
        self,
        model: APIModel,
        _depth: int = -1,
        parent: APIModel | None = None
    ) -> list[tuple[int, BaseReference]]:
        """Traverse the object schema to find references."""
        depth = _depth + 1
        refs: list[tuple[int, BaseReference]] = []
        for name in model.model_fields:
            v = getattr(self, name)
            if isinstance(v, BaseReference):
                refs.append((depth, v))
                continue
            if isinstance(v, APIModel):
                refs.extend(self.get_reference_tree(v, depth, model))
        return refs

    def get_root_types(self, model: type[pydantic.BaseModel]) -> list[type[APIModel]]:
        if not model.model_fields.get('root'):
            return []
        return list(get_args(model.model_fields['root'].annotation))

    def has_state(self, model: type[T]) -> bool:
        return bool(model.model_fields.get('status'))

    def inspect(self, model: type[T]) -> APIVersionedMeta[T]:
        try:
            return getattr(model, '__meta__')
        except AttributeError:
            raise TypeError(
                f"{model.__name__} is not a known type that can be described "
                f"by {type(self).__name__}."
            )

    def is_concrete(self, model: type[APIModel]) -> bool:
        return not any([
            isinstance(x.annotation, TypeVar)
            for x in model.model_fields.values()
        ])

    def is_dirty(self, instance: APIModel) -> bool:
        """Return a boolean if the data maintained in an instance
        must be written back to its primary or origin storage.
        """
        return instance._dirty # type: ignore

    def is_namespaced(self, model: type[BaseResource]) -> bool:
        """Return a boolean indicating if the model is namespaced."""
        return model.__namespaced__

    def is_root(self, model: type[T]):
        return self.inspect(model).root