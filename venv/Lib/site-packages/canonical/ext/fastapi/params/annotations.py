# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Annotated

import fastapi

from canonical.ext.api import APIModelInspector
from canonical.ext.crypto.bases import BaseDEK
from canonical.lib.protocols import ICache
from ..utils import request_state as s
from ..utils import inject_state as d


__all__: list[str] = [
    'AccessPolicyServerURL',
    'DefaultCache',
    'DefaultInspector',
]


AccessPolicyServerURL = Annotated[str, d('core_url')]
DataEncryption = Annotated[BaseDEK, s('dek', BaseDEK)]
DefaultCache = Annotated[ICache, s('cache', ICache, True)]
DefaultInspector = Annotated[APIModelInspector, fastapi.Depends(APIModelInspector)]