# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import AsyncContextManager
from typing import Mapping

import fastapi
import httpx


class ProxiedResponse(fastapi.responses.StreamingResponse):

    def __init__(
        self,
        stream: AsyncContextManager[httpx.Response],
        headers: Mapping[str, str] | None = None,
    ):
        self.stream = stream
        fastapi.Response.__init__(self, content=b'')

    async def stream_response(self, send: Any) -> None:
        async with self.stream as response:
            super().__init__(
                status_code=response.status_code,
                headers={**self.headers, **response.headers},
                content=response.aiter_bytes()
            )
            await send(
                {
                    "type": "http.response.start",
                    "status": response.status_code,
                    "headers": self.raw_headers,
                }
            )
            async for chunk in self.body_iterator:
                if not isinstance(chunk, bytes):
                    chunk = chunk.encode(self.charset)
                await send({"type": "http.response.body", "body": chunk, "more_body": True})

            await send({"type": "http.response.body", "body": b"", "more_body": False})