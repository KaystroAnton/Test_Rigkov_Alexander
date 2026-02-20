# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import uuid
from typing import Any

import fastapi

from canonical.ext.templates import TemplateService


class UserAgentException(Exception):
    template_name: str
    page_heading: str | None = None
    page_title: str | None = None
    status_code: int = 400

    def get_template_names(self) -> list[str]:
        return [self.template_name]

    def get_template_context(self) -> dict[str, Any]:
        return {
            'exception': self,
            'incident_id': str(uuid.uuid4()),
            'page_heading': self.page_heading,
            'page_title': self.page_title
        }

    async def render(
        self,
        templates: TemplateService,
        context: dict[str, Any] | None = None
    ) -> fastapi.Response:
        return fastapi.Response(
            status_code=self.status_code,
            content=await templates.render_template(
                templates=self.get_template_names(),
                context={
                    **(context or {}),
                    **self.get_template_context()
                }
            )
        )