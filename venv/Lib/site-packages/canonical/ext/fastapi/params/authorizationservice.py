# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging

import fastapi

from canonical.ext.iam.protocols import IResourceAuthorizationContext


__all__: list[str] = ['AuthorizationService']

logger: logging.Logger = logging.getLogger('uvicorn')


def AuthorizationService(impl: type[IResourceAuthorizationContext]):
    logger.info("Using %s as authorization implementation.", impl.__name__)

    def f(request: fastapi.Request, ctx: impl = fastapi.Depends(impl)):
        setattr(request.state, 'resource_context', ctx)
        return ctx
    return fastapi.Depends(f)