# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Iterable

import fastapi
import fastapi.params
from fastapi.exceptions import HTTPException

from canonical.utils.http import MediaTypeSelector


def NegotiateResponseMediaType(available: Iterable[str]) -> Any:
    selector = MediaTypeSelector(available)

    def f(
        request: fastapi.Request,
        header: str = fastapi.Header(
            default=...,
            alias='Accept',
            description=(
                "The `Accept` request HTTP header indicates which content "
                "types, expressed as MIME types, the client is able to "
                "understand. The server uses content negotiation to select "
                "one of the proposals and informs the client of the choice "
                "with the `Content-Type` response header."
            ),
            examples=list(available)
        )
    ):
        selected = selector.select(header)
        if selected is None:
            raise HTTPException(
                status_code=406,
                detail=(
                    "Unable to select a response content type based on "
                    "the provided Accept header."
                )
            )
        setattr(request.state, 'media_type', selected)
        return selected

    return fastapi.Depends(f)