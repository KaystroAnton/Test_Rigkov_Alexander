# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Self

import pydantic

from canonical import DomainName
from .bases import BaseNamespace
from .namespacespec import NamespaceSpec


class OrganizationSpec(NamespaceSpec):
    model_config = {'populate_by_name': True}

    id: int | None = pydantic.Field(
        default=None,
        title="Organization ID",
        description=(
            "A numeric identifier for this organization. This field is "
            "auto-generated and can not be set or changed."
        ),
        frozen=True
    )

    display_name: str = pydantic.Field(
        default=...,
        alias='displayName',
        description=(
            "The display name of the `Organization` for user "
            "interfaces."
        )
    )

    domain: DomainName | None = pydantic.Field(
        default=None,
        description=(
            "The verified domain name for this organization."
        )
    )


class Organization(
    BaseNamespace[str],
    group='',
    version='v1',
    plural='organizations',
    type='webiam.io/organization'
):
    model_config = {'populate_by_name': True}

    spec: 'OrganizationSpec' = pydantic.Field(
        default=...,
        description="Defines the behavior of the `Namespace`."
    )

    def can_change(self, old: Self) -> bool:
        if not super().can_change(old):
            return False
        return all([
            self.spec.id == old.spec.id
        ])