# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import inspect
from typing import cast
from typing import Any
from typing import Generic
from typing import TypeVar

from canonical.lib.protocols import IBuilder
from canonical.utils import class_property
from canonical.utils import merge_signatures


P = TypeVar('P')
T = TypeVar('T', covariant=True)


class ParameterizedBuilder(IBuilder[T], Generic[T, P]):
    __module__: str = 'canonical.ext.builder'
    _params: dict[str, Any]

    @property
    def params(self) -> P:
        return cast(P, self._params)

    @class_property
    def __signature__(cls) -> inspect.Signature:
        return merge_signatures([
            inspect.signature(cls.__init__),
            inspect.signature(getattr(cls, 'setup', lambda: None))
        ])

    def __init__(self):
        self._params = {}

    def set_param(self, name: str, value: Any):
        self._params[name] = value

    async def build(self) -> T:
        raise NotImplementedError