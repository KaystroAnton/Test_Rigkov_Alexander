# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

import pydantic


class ListMeta(pydantic.BaseModel):
    """Standard list metadata."""
    model_config = {'populate_by_name': True}

    next_page: str | None = pydantic.Field(
        default=None,
        title='Continue',
        alias='nextPage',
        description=(
            "continue may be set if the user set a limit on the number of items "
            "returned, and indicates that the server has more data available. "
            "The value is opaque and may be used to issue another request to "
            "the endpoint that served this list to retrieve the next set of "
            "available objects. Continuing a consistent list may not be possible "
            "if the server configuration has changed or more than a few minutes "
            "have passed. The resourceVersion field returned when using this "
            "continue value will be identical to the value in the first response, "
            "unless you have received this token from an error message."
        )
    )

    resource_version: str = pydantic.Field(
        default='',
        alias='resourceVersion',
        description=(
            "String that identifies the server's internal version of this object that "
            "can be used by clients to determine when objects have changed. Value "
            "must be treated as opaque by clients and passed unmodified back to the "
            "server. Populated by the system. Read-only."
        )
    )

    @classmethod
    def default(cls):
        return cls()