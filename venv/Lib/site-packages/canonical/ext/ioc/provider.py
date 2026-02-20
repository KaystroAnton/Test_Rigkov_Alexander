# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dependency import Dependency
    from .requirement import Requirement


class DependencyProvider:
    dependencies: dict[str, 'Dependency']
    requirements: dict[str, 'Requirement']

    def __init__(self):
        self.requirements = {}
        self.dependencies = {}

    def inject(self):
        for requirement in self.requirements.values():
            requirement.inject(self.dependencies[requirement.name])

    def require(self, requirement: Requirement):
        self.requirements[requirement.name] = requirement

    def provide(self, dependency: Dependency):
        self.dependencies[dependency.name] = dependency


__provider = DependencyProvider()
inject = __provider.inject
require = __provider.require
provide = __provider.provide