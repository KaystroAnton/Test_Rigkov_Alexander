# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .bases import BaseNamespace
from .hierarchicalnamespacespec import HierarchicalNamespaceSpec
from .refs import ProjectParentReference


class Project(
    BaseNamespace[str],
    group='',
    version='v1',
    plural='projects',
    type='webiam.io/project'
):
    model_config = {'populate_by_name': True}

    spec: HierarchicalNamespaceSpec[ProjectParentReference] = pydantic.Field(
        default_factory=HierarchicalNamespaceSpec,
        description="Defines the behavior of the `Namespace`."
    )