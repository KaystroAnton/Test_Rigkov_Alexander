# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


class HTTPRequestModelMixin:
    _method: str | None = None
    _url: str | None = None
    #method: str = pydantic.Field(
    #    default=None,
    #    exclude=True
    #)

    #url: str | None = pydantic.Field(
    #    default=None,
    #    exclude=True
    #)

    def with_endpoint(self, method: str, endpoint: str):
        self._method = method
        self._url = endpoint
        return self