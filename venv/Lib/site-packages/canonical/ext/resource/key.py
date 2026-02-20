# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Generic
from typing import TypeVar


__all__: list[str] = [
    'KeyFactory'
]

M = TypeVar('M')


class Key(Generic[M]):

    def __iter__(self):
        return iter((None, None))


class KeyFactory(Generic[M]):
    model: type[M]

    def __init__(self, model: type[M]):
        self.model = model