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
from .namespacespec import NamespaceSpec


class Namespace(
    BaseNamespace[str],
    group='',
    version='v1',
    plural='namespaces',
    type='webiam.io/namespace'
):
    model_config = {'populate_by_name': True}

    spec: NamespaceSpec = pydantic.Field(
        default_factory=NamespaceSpec,
        description="Defines the behavior of the `Namespace`."
    )