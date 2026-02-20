# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from canonical.ext.fastapi.mixins import QueryModelMixin
from canonical.lib import FormDataModel

from .annotations import AuthorizationCode
from .annotations import Issuer
from .annotations import State


class AuthorizationResponse(FormDataModel, QueryModelMixin):
    model_config = {'extra': 'forbid'}
    code: AuthorizationCode = None
    iss: Issuer = None
    state: State = None