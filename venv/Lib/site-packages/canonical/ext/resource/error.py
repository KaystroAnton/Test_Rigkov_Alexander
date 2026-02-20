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

from canonical.utils.http import Request
from .resource import Resource
from .transientmeta import TransientMeta


S = TypeVar('S')


class ErrorData(pydantic.BaseModel):
    model_config = {'populate_by_name': True}

    detail: str = pydantic.Field(
        default=...,
        description="A summary of the error."
    )


class HTTPErrorData(ErrorData, Generic[S]):
    status_code: S = pydantic.Field(
        default=...,
        alias='statusCode',
        description=(
            "The HTTP status code identifying the error state."
        )
    )

    request: Request = pydantic.Field(
        default=...,
        description=(
            "Describes the HTTP request that caused the error "
            "condition."
        )
    )


class FieldError(pydantic.BaseModel):
    model_config = {'populate_by_name': True}

    document_path: str = pydantic.Field(
        default='',
        alias='documentPath',
        description=(
            "A valid JSON Patch path to the invalid field."
        )
    )

    message: str = pydantic.Field(
        default=...,
        description="A summary of the error."
    )

    schema_path: tuple[int | str, ...] = pydantic.Field(
        default=...,
        alias='schemaPath',
        description=(
            "A sequence containing the path to the invalid "
            "field."
        )
    )

    data: Any = pydantic.Field(
        default=...,
        description="The invalid data as provided by the client."
    )

    type: str

    @pydantic.model_validator(mode='before')
    def preprocess(cls, values: dict[str, Any]):
        p: tuple[int | str, ...] | None = values.get('schema_path')
        if p is not None:
            # TODO: move to common lib
            d = ''
            for c in p:
                d += '/'
                if not isinstance(c, str):
                    d += str(c)
                    continue
                c = str.replace(c, '~', '~0')
                c = str.replace(c, '/', '~1')
                d += c
            values['document_path'] = d
        return values


class ObjectValidationErrorData(HTTPErrorData[Literal[422]]):
    model_config = {'populate_by_name': True}
    field_errors: list[FieldError] = pydantic.Field(
        default=...,
        alias='fieldErrors',
        min_length=1
    )



class Error(Resource[TransientMeta], version='errors/v1'):
    model_config = {'populate_by_name': True}
    data: ObjectValidationErrorData | HTTPErrorData[int] | ErrorData

    @classmethod
    def factory(cls, data: dict[str, Any]):
        return cls.model_validate({
            'metadata': {},
            'data': data
        })