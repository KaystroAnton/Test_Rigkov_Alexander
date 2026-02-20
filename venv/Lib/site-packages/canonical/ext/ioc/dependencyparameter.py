# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Union

import pydantic

from .dependencyreference import DependencyReference


LiteralType = Union[str, int, float, bool, list[Any]]


class DependencyParameter(pydantic.RootModel[DependencyReference | LiteralType]):

    def is_reference(self) -> bool:
        return isinstance(self.root, DependencyReference)

    def resolve(self):
        if self.is_reference():
            raise NotImplementedError
        return self.root