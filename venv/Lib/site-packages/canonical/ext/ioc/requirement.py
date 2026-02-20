# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi.params

from .dependency import Dependency
from .provider import require


class Requirement(fastapi.params.Depends):

    def __init__(self, name: str):
        self.name = name
        require(self)

    def inject(self, dep: Dependency) -> None:
        super().__init__(dependency=dep.build(), use_cache=True)