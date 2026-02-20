# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Callable


NOT_AVAILABLE = object()


class Deferred:

    def __init__(self, resolve: Callable[[], Any]):
        self.__resolve = resolve
        self.__result = NOT_AVAILABLE

    def __str__(self) -> str:
        if self.__result == NOT_AVAILABLE:
            self.__result = self.__resolve()
        return str(self.__result)

    def __getattr__(self, attname: str) -> Any:
        if self.__result == NOT_AVAILABLE:
            self.__result = self.__resolve()
        return getattr(self.__result, attname)