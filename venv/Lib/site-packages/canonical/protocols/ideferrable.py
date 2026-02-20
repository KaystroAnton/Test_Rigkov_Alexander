# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import cast
from typing import Callable
from typing import TypeVar
from typing import Protocol

from canonical.utils import Deferred


T = TypeVar('T')


class IDeferrable(Protocol):
    __module__: str = 'canonical.protocols'

    @classmethod
    def defer(cls: T, resolve: Callable[[], T]) -> T:
        return cast(T, Deferred(resolve))