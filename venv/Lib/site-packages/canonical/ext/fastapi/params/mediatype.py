# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Annotated
from typing import Iterable

import fastapi
import fastapi.params
from fastapi.exceptions import HTTPException

from canonical.utils.http import MediaTypeSelector


def MediaType(available: Iterable[str]) -> Annotated[type[str], fastapi.params.Depends]:
    selector = MediaTypeSelector(available)

    def f(request: fastapi.Request):
        header = request.headers.get('Accept')
        if header is None:
            raise HTTPException(
                status_code=406,
                detail="The Accept header is required."
            )
        selected = selector.select(header)
        if selected is None:
            raise HTTPException(
                status_code=406,
                detail=(
                    "Unable to select a response content type based on "
                    "the provided Accept header."
                )
            )
        return selected

    return Annotated[str, fastapi.Depends(f)]