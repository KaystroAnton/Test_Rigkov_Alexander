# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import collections
import inspect
from typing import cast
from typing import Any

import fastapi
import fastapi.params
import pydantic


class QueryModelMixin:

    @classmethod
    def as_query(cls) -> Any:
        """Create a :class:`fastapi.params.Depends` instance
        that obtains the models' input fields from query
        parameters.
        """
        cls = cast(type[pydantic.BaseModel], cls)
        def f(request: fastapi.Request, **kwargs: Any):
            return cls.model_validate(request.query_params)

        sig = inspect.signature(f)
        params: dict[str, inspect.Parameter] = collections.OrderedDict({
            'request': sig.parameters['request']
        })
        for attname, field in cls.model_fields.items():
            if attname == 'request':
                raise ValueError(
                    f"{cls.__name__} specifies the field 'request', which is "
                    "a reserved name."
                )
            if not field.annotation or field.exclude:
                continue
            params[attname] = inspect.Parameter(
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                name=attname,
                annotation=field.annotation,
                default=fastapi.Query(
                    default=field.default,
                    default_factory=field.default_factory,
                    alias=field.alias,
                    title=field.title,
                    description=field.description
                )
            )

        setattr(f, '__signature__', sig.replace(parameters=list(params.values())))
        return fastapi.Depends(f)