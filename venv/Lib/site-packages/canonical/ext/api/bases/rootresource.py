# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import cast
from typing import TypeVar

import pydantic

from .resource import BaseResource


T = TypeVar('T')


class BaseRootResource(pydantic.RootModel[T], BaseResource):

    def replacable(self) -> bool:
        return cast(BaseResource, self.root).replacable()

    def replace(self, instance: pydantic.BaseModel):
        return cast(BaseResource, self.root).replace(instance)