# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import ClassVar
from typing import Self
from typing import TypeVar

import pydantic
import pydantic.fields

from canonical.ext.api.protocols import IObjectIdentifier


T = TypeVar('T')


class BaseReference:
    _default_reference_model: ClassVar[type[Any] | None] = None
    _reference_model: type[Any] | None = pydantic.PrivateAttr(default_factory=lambda: None)

    @classmethod
    def __init_subclass__(cls, ref: type | None = None):
        if ref is not None:
            cls._default_reference_model = ref

    @property
    def scalar(self) -> int | str:
        raise NotImplementedError

    def attach_to_namespace(self, namespace: str) -> Self:
        raise NotImplementedError

    def as_name(self) -> int | str:
        raise NotImplementedError

    def get_model(self) -> type[Any]:
        model = self._reference_model or self._default_reference_model
        if model is None or isinstance(model, pydantic.fields.ModelPrivateAttr):
            raise TypeError(f"{type(self).__name__} is not attached to a model.")
        return model

    def get_namespace(self) -> str | None:
        raise NotImplementedError(
            f'{type(self).__name__}.get_namespace() is not implemented.'
        )

    def has_model(self) -> bool:
        return self._reference_model is not None

    def in_namespace(self, namespace: str) -> bool:
        raise NotImplementedError

    def is_cluster(self) -> bool:
        raise NotImplementedError

    def is_local(self) -> bool:
        raise NotImplementedError

    def is_namespaced(self) -> bool:
        raise NotImplementedError

    def with_model(self, model: type[T]) -> IObjectIdentifier[T]:
        self._reference_model = model
        return self

    def with_namespace(self, namespace: str) -> Self:
        raise NotImplementedError