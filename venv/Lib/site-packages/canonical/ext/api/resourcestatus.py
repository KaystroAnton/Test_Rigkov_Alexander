# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
from typing import Any

import pydantic

from .apimodel import APIModel
from .objectmeta import ObjectMeta


class ResourceStatus(APIModel):
    changed: datetime.datetime = pydantic.Field(
        default=...,
        description=(
            "The date and time of the last change to this {kind}."
        )
    )

    version: int = pydantic.Field(
        default=...,
        description=(
            "Current version of the {kind}."
        )
    )

    message: str = pydantic.Field(
        default=...,
        description="The message of the last known condition."
    )

    current: str = pydantic.Field(
        default=...,
        description="The status of the last known condition."
    )

    def update(
        self,
        metadata: ObjectMeta[Any],
        status: str,
        **kwargs: Any
    ) -> None:
        self.changed = datetime.datetime.now(datetime.timezone.utc)
        self.current = status
        self.version = metadata.generation
        for attname, value in kwargs.items():
            setattr(self, attname, value)