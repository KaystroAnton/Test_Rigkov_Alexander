# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import os
from typing import Any

import fastapi
import fastapi.params

from canonical.exceptions import ProgrammingError
from canonical.ext.resource import IResourceRepository
from .proxiedresponse import ProxiedResponse
from .resourceapplication import ResourceApplication
from .resourceclient import ResourceClient
from .resourcerouter import ResourceRouter
from .utils import inject
from .utils import requires


__all__: list[str] = [
    'inject',
    'requires',
    'EnvironmentVariable',
    'ProxiedResponse',
    'ResourceApplication',
    'ResourceClient',
    'ResourceRouter'
]

def setup_dependencies(
    repository: type[IResourceRepository[Any]]
):
    async def f(
        request: fastapi.Request,
        resources: IResourceRepository[Any] = fastapi.Depends(repository)
    ):
        setattr(request.state, 'resources', resources)

    return [fastapi.Depends(f)]


def EnvironmentVariable(name: str, required: bool = True):
    def f(request: fastapi.Request):
        try:
            return os.environ[name]
        except KeyError:
            if required:
                raise ProgrammingError(
                    f"Dependency {name} is requested from environment "
                    "but it was not present."
                )
            return None

    return fastapi.Depends(f)