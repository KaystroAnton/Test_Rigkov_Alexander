# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable
from typing import Literal

import pydantic

from canonical.lib.types import PythonSymbol
from .dependencyparameter import DependencyParameter


class Dependency(pydantic.BaseModel):
    kind: Literal['instance', 'factory'] = 'factory'
    _dependency: Any = None
    name: str
    ref: PythonSymbol[Any] = pydantic.Field(
        alias='symbol'
    )
    args: list[DependencyParameter] = []
    kwargs: dict[str, DependencyParameter] = {}

    def build(self):
        """Build the dependency and return a callable that
        is injectable.
        """
        if self._dependency is None:
            injectable = None
            match self.kind:
                case 'instance': injectable = self.build_instance()
                case _:
                    raise NotImplementedError
            assert injectable is not None
            self._dependency = injectable
        return self._dependency

    def build_instance(self) -> Callable[..., Any]:
        """Build a singleton that lives throughout the application
        lifecycle.
        """
        args: list[Any] = [arg.resolve() for arg in self.args]
        kwargs: dict[str, Any] = {k: v.resolve() for k, v in self.kwargs.items()}
        instance = self.ref.value(*args, **kwargs)
        return lambda: instance