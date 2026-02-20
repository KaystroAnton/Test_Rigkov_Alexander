# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from canonical.ext.api import APIRootResourceModel
from .domain import Domain
from .organization import Organization
from .project import Project
from .namespace import Namespace as NamespaceType


class Namespace(
    APIRootResourceModel[Organization | Project | Domain | NamespaceType],
    group='',
    version='v1',
    plural='namespaces',
    short='ns'
):
    """A `Namespace` provides a mechanism for isolating groups of resources.
    Names of resources need to be unique within a namespace, but not across
    namespaces. Namespace-based scoping is applicable only for namespaced
    objects and not for system-wide objects
    """
    model_config = {'populate_by_name': True}

    @property
    def spec(self):
        return self.root.spec

    @property
    def type(self):
        return self.root.type

    def is_organization(self) -> bool:
        return self.root.type == 'webiam.io/organization'