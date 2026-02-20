# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Generic
from typing import Literal
from typing import TypeVar

import pydantic

from .listmeta import ListMeta


K = TypeVar('K')
R = TypeVar('R')


class ListBase(pydantic.BaseModel, Generic[K, R]):
    """List base class."""
    model_config = {'populate_by_name': True}

    api_version: Literal['v1'] = pydantic.Field(
        default=...,
        alias='apiVersion',
        title="API Version",
        description=(
            "The `apiVersion` field defines the versioned schema of this "
            "representation of an object. Servers should convert recognized "
            "schemas to the latest internal value, and may reject "
            "unrecognized values."
        )
    )

    kind: K = pydantic.Field(
        default=...,
        description=(
            "Kind is a string value representing the REST resource this "
            "object represents. Servers may infer this from the endpoint "
            "the client submits requests to. Cannot be updated. In `CamelCase`."
        )
    )

    metadata: ListMeta = pydantic.Field(
        default=...,
        description="Standard list metadata."
    )

    items: list[R] = []