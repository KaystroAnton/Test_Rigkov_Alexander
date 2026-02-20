# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Generic
from typing import Protocol
from typing import TypeVar


T = TypeVar('T')


class IObjectIdentifier(Protocol, Generic[T]):

    def get_model(self) -> type[T]: ...
    def get_namespace(self) -> str | None: ...
    def has_model(self) -> bool: ...
    def with_model(self, model: T) -> 'IObjectIdentifier[T]': ...