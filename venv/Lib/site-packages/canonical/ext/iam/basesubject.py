# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Literal
from typing import Generic
from typing import TypeVar

import pydantic


N = TypeVar('N')
K = TypeVar('K')


class BaseSubject(pydantic.BaseModel, Generic[K, N]):
    api_group: Literal['iam.webiam.io'] = pydantic.Field(
        default='iam.webiam.io',
        alias='apiGroup',
        description=(
            "Must be `iam.webiam.io` for `User`, `ServiceAccount` and "
            "`Group` references."
        )
    )

    kind: K = pydantic.Field(
        default=...,
        description=(
            "Kind of object being referenced. Values defined by this API "
            "group are `User`, `Group`, `ServiceAccount` and `Domain`. If the "
            "Authorizer does not recognized the kind value, the Authorizer "
            "must report an error."
        )
    )

    name: N = pydantic.Field(
        default=...,
        description=(
            "Name of the object being referenced."
        )
    )

    namespace: str | None = pydantic.Field(
        default=None,
        description=(
            "Namespace of the referenced object. If the object kind is "
            "non-namespace, such as `User` or `Group`, and this value "
            "is not empty the Authorizer must report an error."
        )
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        cls.model_config['title'] = cls.__name__
        cls.model_rebuild()

    def model_post_init(self, _: Any) -> None:
        assert isinstance(self.kind, str)
        if self.kind in {'User', 'Group', 'ServiceAccount'} and self.namespace:
            raise ValueError("Namespace must be unset.")