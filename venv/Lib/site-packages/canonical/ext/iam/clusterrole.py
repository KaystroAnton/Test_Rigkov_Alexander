# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .baserole import BaseRole


class ClusterRole(
    BaseRole,
    kind='ClusterRole',
    group='iam.webiam.io',
    version='v1',
    plural='clusterroles',
):

    @classmethod
    def is_namespaced(cls) -> bool:
        return False