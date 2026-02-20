# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Generic
from typing import TypeVar

import pydantic

from ..bases import BaseBuilder


T = TypeVar('T', bound=pydantic.BaseModel)


class BaseModelClassBuilder(BaseBuilder[T], Generic[T]):
    children: list[type[pydantic.BaseModel]]

    def rebuild(self):
        assert self.model.model_rebuild(force=True)
        self.fields = self.model.model_fields

    def setup(self, model: type[T], **kwargs: Any) -> None: # type: ignore
        self.fields = model.model_fields

    def set_field_annotation(self, model: pydantic.BaseModel, name: str, annotation: Any):
        model.model_fields[name].annotation = annotation