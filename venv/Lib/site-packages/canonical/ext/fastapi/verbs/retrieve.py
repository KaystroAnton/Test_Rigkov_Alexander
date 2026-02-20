# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TypeVar

from canonical.ext.api import APIResourceType
from ..params import RequestResource
from .default import Default


T = TypeVar('T', bound=APIResourceType)


class Retrieve(Default[T]):
    detail = True
    existing = True
    method = 'GET'
    status_code = 200
    verb = 'get'


    async def handle(self, obj: RequestResource) -> Any:
        return obj

    def get_endpoint_summary(self) -> str:
        return f'Retrieve a specific {self.model.__name__}'

    def get_openapi_responses(self) -> dict[int, dict[str, Any]]:
        return {
            **super().get_openapi_responses(),
            200: {
                'model': self.model,
                'description': self.get_response_description()
            }
        }

    def get_response_description(self) -> str:
        return f"{self.model.__name__} object."