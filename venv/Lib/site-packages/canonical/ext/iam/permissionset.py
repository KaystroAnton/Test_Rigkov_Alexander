# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from canonical.ext.resource import Resource
from canonical.ext.resource import TransientMeta


class PermissionSet(
    Resource[TransientMeta],
    version='permissionsets.iam.webiam.io/v1'
):
    granted: set[str] = pydantic.Field(
        default_factory=set,
        description=(
            "The set of permissions that are granted on a "
            "resource."
        ),
    )