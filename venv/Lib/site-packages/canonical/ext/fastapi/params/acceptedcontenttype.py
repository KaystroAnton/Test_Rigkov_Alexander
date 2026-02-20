# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Iterable

import fastapi
import fastapi.params
from fastapi.exceptions import HTTPException

from canonical.utils.http import MediaTypeSelector


def AcceptedContentType(available: Iterable[str]) -> fastapi.params.Depends:
    selector = MediaTypeSelector(available)

    def f(
        header: str = fastapi.Header(
            default=...,
            alias='Content-Type',
            description=(
                "The `Content-Type` representation header is used to indicate "
                "the original media type of the resource (prior to any "
                "content encoding applied for sending)."
            ),
            examples=list(available)
        )
    ):
        selected = selector.select(header)
        if selected is None:
            raise HTTPException(
                status_code=415,
                detail=(
                    "The server refuses to accept the request because "
                    "the payload format is in an unsupported format."
                )
            )
        return selected

    return fastapi.Depends(f)