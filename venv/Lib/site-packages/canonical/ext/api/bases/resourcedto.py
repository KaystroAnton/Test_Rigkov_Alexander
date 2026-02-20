# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import cast
from typing import Any
from typing import Generic
from typing import TypeVar

import pydantic

from ..fields import APIVersion
from ..fields import Kind


T = TypeVar('T')


class BaseResourceDTO(pydantic.BaseModel, Generic[T]):
    api_version: APIVersion
    kind: Kind

    @property
    def key(self) -> Any:
        raise NotImplementedError

    @property
    def model(self) -> type[T]:
        raise NotImplementedError

    def factory(self, uid: int) -> T:
        # TODO
        model = cast(type[pydantic.BaseModel], self.model)
        data = self.model_dump()
        data['metadata']['generation'] = 1
        data['metadata']['uid'] = uid
        return cast(T, model.model_validate(data))