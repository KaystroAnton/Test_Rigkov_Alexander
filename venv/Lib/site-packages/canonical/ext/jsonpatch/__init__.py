# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal
from typing import Union

import pydantic


JSONPatchOperationType = Literal[
    'add',
    'replace',
    'remove',
    'move',
    'copy',
    'test'
]


class JSONPatchValueOperation(pydantic.BaseModel):
    op: Literal['add', 'replace', 'test'] = pydantic.Field(
        default=...,
        description=(
            "The operation to be applied to the target JSON document. "
            "Must be `add`, `replace` or `test`."
        )
    )

    path: str = pydantic.Field(
        default=...,
        description=(
            "Path to apply the patch to in the target JSON document. "
            "Must start with a slash."
        )
    )


class JSONPatchMoveOperation(pydantic.BaseModel):
    op: Literal['move'] = pydantic.Field(
        default=...,
        description=(
            "The operation to be applied to the target JSON document. "
            "Must be `move`."
        )
    )

    path: str = pydantic.Field(
        default=...,
        description=(
            "Path in the target document to move `from`."
        )
    )

    source: str = pydantic.Field(
        default=...,
        alias='from',
        description=(
            "Source path in the target JSON document."
        )
    )



class JSONPatchCopyOperation(pydantic.BaseModel):
    op: Literal['copy'] = pydantic.Field(
        default=...,
        description=(
            "The operation to be applied to the target JSON document. "
            "Must be `copy`."
        )
    )

    path: str = pydantic.Field(
        default=...,
        description=(
            "Path in the target document to copy `from`."
        )
    )

    source: str = pydantic.Field(
        default=...,
        alias='from',
        description=(
            "Source path in the target JSON document."
        )
    )


class JSONPatchRemoveOperation(pydantic.BaseModel):
    op: Literal['remove'] = pydantic.Field(
        default=...,
        description=(
            "The operation to be applied to the target JSON document. "
            "Must be `remove`."
        )
    )

    path: str = pydantic.Field(
        default=...,
        description=(
            "Path to remove from the target JSON document."
        )
    )


JSONPatchType = Union[
    JSONPatchValueOperation,
    JSONPatchCopyOperation,
    JSONPatchMoveOperation,
    JSONPatchRemoveOperation
]