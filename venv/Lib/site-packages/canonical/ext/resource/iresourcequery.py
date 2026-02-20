# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import AsyncIterable
from typing import Generator
from typing import Generic
from typing import TypeVar

import pydantic

from .resource import Resource
from .rootresource import RootResource


R = TypeVar('R', bound=Resource[Any] | RootResource[Any])
K = TypeVar('K')
T = TypeVar('T', bound=pydantic.BaseModel)


class IResourceQuery(AsyncIterable[K], Generic[K]):

    def __await__(self) -> Generator[None, None, list[K]]:
        ...