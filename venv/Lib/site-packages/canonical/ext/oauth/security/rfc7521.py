# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi
import pydantic
from fastapi.security.base import SecurityBase
from fastapi.openapi.models import SecurityBase as SecurityBaseModel
from fastapi.openapi.models import SecuritySchemeType

from canonical.ext.oauth.models import ClientAssertion
from canonical.ext.oauth.utils import DefaultMediaTypeSelector


class RFC7521(SecurityBase):
    selector = DefaultMediaTypeSelector

    def __init__(
        self,
        scheme_name: str,
        description: str | None = None,
    ):
        self.model = SecurityBaseModel(
            type=SecuritySchemeType.oauth2,
            description=description,
        )
        self.scheme_name = scheme_name or self.__class__.__name__

    async def __call__(self, request: fastapi.Request) -> ClientAssertion | None:
        try:
            assertion = ClientAssertion.model_validate_json(await request.json())
        except pydantic.ValidationError:
            assertion = None
        return assertion