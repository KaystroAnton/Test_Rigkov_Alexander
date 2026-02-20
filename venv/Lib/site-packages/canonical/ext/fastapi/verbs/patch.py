# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from canonical.ext.resource import Error
from canonical.ext.jsonpatch import JSONPatchType
from .default import Default


class Patch(Default[Any]):
    detail = True
    exists = True
    input_model = JSONPatchType
    method = 'PATCH'
    requires_body = True
    verb = 'patch'

    def get_openapi_responses(self) -> dict[int, Any]:
        return {
            **super().get_openapi_responses(),
            409: {
                'model': Error,
                'description': (
                    f'One or more of the patches can not be applied to the {self.model.__name__}.'
                )
            }
        }