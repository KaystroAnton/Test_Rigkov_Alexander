# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
from typing import cast
from typing import overload
from typing import Generic
from typing import TypeVar


T = TypeVar('T', bound=int | str)


class ReferenceDescriptor(Generic[T]):

    def __init__(self, attname: str) -> None:
        self.attname = attname

    @overload
    def __get__(self, obj: None, cls: None) -> ReferenceDescriptor[T]:
        ...

    @overload
    def __get__(self, obj: object, cls: type[object]) -> T:
        ...

    def __get__(
        self, obj: object | None, cls: type[object] | None = None
    ) -> ReferenceDescriptor[T] | T:
        if obj is None:
            return self
        return cast(T, obj.__dict__[self.attname])