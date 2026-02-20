# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from collections import OrderedDict
from inspect import Parameter
from inspect import Signature
from typing import Any
from typing import TypeVar

import fastapi

from canonical.ext.resource import Error
from canonical.ext.resource import ResourceType
from ..response import Response
from .detail import Detail


T = TypeVar('T')


class Replace(Detail[T]):
    detail = True
    existing = True
    method = 'PUT'
    requires_body = True
    verb = 'replace'

    def annotate_handler(self, signature: Signature) -> Signature:
        params: OrderedDict[str, Parameter] = OrderedDict(signature.parameters)
        for name, param in signature.parameters.items():
            if param.annotation == self.model:
                params[name] = param.replace(annotation=self.get_input_model())
                self.input_params.add(name)
                continue
        return signature.replace(parameters=list(params.values()))

    def can_replace(self, resource: ResourceType) -> bool:
        return resource.replacable()

    def get_endpoint_summary(self) -> str:
        return f'Replace an existing {self.model.__name__}'

    def get_openapi_responses(self) -> dict[int, Any]:
        return {
            **super().get_openapi_responses(),
            409: {
                'model': Error,
                'description': (
                    f'The {self.model.__name__} identified by the path parameters '
                    'can not be replaced.'
                )
            }
        }

    def get_response_description(self) -> str:
        return f"The latest version of the {self.model.__name__} object."

    def replaces(self) -> bool:
        return True

    async def render_to_response(
        self,
        request: fastapi.Request,
        result: Any,
        media_type: str
    ) -> Response[Any]:
        if not isinstance(result, self.model):
            raise TypeError(
                f"Function handle() must return a {self.model.__name__} "
                f"instance, got {type(result).__name__}."
            )
        return Response(
            media_type=media_type,
            status_code=205,
            content=result
        )