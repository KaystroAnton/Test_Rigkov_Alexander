# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
from typing import cast
from typing import Any
from typing import Generic
from typing import TypeVar

import pydantic

from .resourcestate import CurrentResourceState
from .resourcestate import ResourceState
from .versionedresource import VersionedResource


C = TypeVar('C', bound=ResourceState[Any] | CurrentResourceState)
S = TypeVar('S', bound=pydantic.BaseModel)


class TransitioningResource(VersionedResource[S], Generic[S, C]):
    status: C = pydantic.Field(
        default=None,
        description=(
            "Describes the current state of the resource. "
        ),
    )

    def _initialize_status(self) -> None:
        status = self.initialize_status()
        if status is None:
            field = self.model_fields['status']
            adapter = cast(
                pydantic.TypeAdapter[C],
                pydantic.TypeAdapter(field.annotation)
            )
            status = adapter.validate_python({})
        self.status = status

    def initialize_status(self) -> C | None:
        return None

    def model_post_init(self, _: Any) -> None:
        if self.status is None: # type: ignore
            self._initialize_status()

    def set_status(
        self,
        status: str,
        *,
        timestamp: datetime.datetime | None = None,
        message: str = '',
        **params: Any
    ) -> C:
        self.logger.debug(
            "%s status changed (pk: %s, status: %s, message: %s)",
            type(self).__name__,
            self.pk,
            status,
            message
        )
        return self.status.new(
            status=status,
            generation=self.metadata.generation,
            message=message,
            timestamp=timestamp or datetime.datetime.now(datetime.timezone.utc),
            **{**self.new_status_params(), **params}
        )

    def new_status_params(self) -> dict[str, Any]:
        return {}