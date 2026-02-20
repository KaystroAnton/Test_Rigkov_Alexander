# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from canonical.lib.utils.encoding import b64encode
from canonical.ext.api import ClusterObjectReference
from .bases import BaseClient
from .clientspec import ClientSpec


class ClusterClient(
    BaseClient[ClientSpec[ClusterObjectReference]],
    group='oauth',
    version='v2',
    plural='clusterclients',
    namespaced=False
):

    @property
    def id(self) -> str:
        return b64encode(f'clusterclients::{self.metadata.name}', encoder=str)