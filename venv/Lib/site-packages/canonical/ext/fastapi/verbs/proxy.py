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

from pydantic.main import BaseModel

from canonical.ext.resource import Error
from .default import Default


T = TypeVar('T')


class Proxy(Default[T]):
    detail: bool = True
    existing: bool = True
    include_in_schema: bool = False

    def get_endpoint_summary(self) -> str:
        return "Proxy request to a remote service"

    def get_response_description(self) -> str:
        return "Response from the remote service"

    def get_response_model(self) -> type[BaseModel] | None:
        return None

    def get_openapi_responses(self) -> dict[int, dict[str, Any]]:
        return {
            511: {
                'model': Error,
                'description': {
                    'Authentication is required to obtain access to the '
                    'upstream service.'
                }
            }
        }

    def get_request_methods(self) -> list[str]:
        return [
            'OPTIONS',
            'HEAD',
            'GET',
            'POST',
            'PUT',
            'DELETE',
            'PATCH',
            # Not supported by FastAPI
            # 'TRACE',
        ]