# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import get_args
from typing import Any
from typing import Generic
from typing import TypeVar

import pydantic

from .basemodelclass import BaseModelClassBuilder


T = TypeVar('T', bound=pydantic.RootModel[Any])


class RootModelBuilder(BaseModelClassBuilder[T], Generic[T]):
    children: list[type[pydantic.BaseModel]]

    def setup(self, model: type[T], **kwargs: Any) -> None: # type: ignore
        super().setup(model, **kwargs)
        self.field = model.model_fields['root']
        self.children = list(get_args(self.field.annotation))
        