# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pydantic

from canonical.ext.resource import Resource
from canonical.ext.resource import TransientMeta


class PermissionQuerySpec(pydantic.BaseModel):
    permissions: set[str] = pydantic.Field(
        default=...,
        description=(
            "The set of permissions that are being requested on a "
            "resource."
        )
    )


class PermissionQuery(Resource[TransientMeta], version='permissionqueries.iam.webiam.io/v1'):
    spec: PermissionQuerySpec = pydantic.Field(
        default=...,
        description=(
            "Specifies the properties of the authorization that "
            "the client wants to know."
        )
    )

    @classmethod
    def factory(cls, spec: dict[str, Any]):
        return cls.model_validate({
            'metadata': {},
            'spec': spec
        })