# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Annotated
from typing import TypeAlias

import fastapi

from canonical.ext.resource import ObjectReference
from canonical.ext.resource import ResourceInspector
from .resourcemodel import ResourceModel


inspector = ResourceInspector()


def get(
    request: fastapi.Request,
    model: ResourceModel
):
    state = request.state
    if not hasattr(state, 'name'):
        return None
    meta = inspector.inspect(model)
    ref = ObjectReference(
        api_version=meta.api_version,
        kind=meta.kind,
        name=getattr(state, 'name'),
        namespace=getattr(state, 'namespace', '')
    )
    return ref.with_model(model)


RequestObjectReference: TypeAlias = Annotated[
    ObjectReference | None,
    fastapi.Depends(get)
]