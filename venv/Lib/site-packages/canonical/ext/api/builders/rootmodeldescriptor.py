# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
from typing import Any
from typing import cast
from typing import overload
from typing import Generic
from typing import TypeVar

import pydantic


T = TypeVar('T')


class RootModelDescriptor(Generic[T]):

    def __init__(self, attname: str) -> None:
        self.attname = attname

    @overload
    def __get__(self, obj: None, cls: None) -> RootModelDescriptor[T]:
        ...

    @overload
    def __get__(self, obj: pydantic.RootModel[Any], cls: type[pydantic.RootModel[Any]]) -> T:
        ...

    def __get__(
        self,
        obj: pydantic.RootModel[Any] | None,
        cls: type[pydantic.RootModel[Any]] | None = None
    ) -> RootModelDescriptor[T] | T:
        if obj is None:
            return self
        return cast(T, obj.root.__dict__[self.attname])