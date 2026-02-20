# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic


__all__: list[str] = [
    'ResourceOptions'
]


class ResourceOptions(pydantic.BaseModel):
    methods: list[str] = pydantic.Field(
        default_factory=list,
        description=(
            "The list of allowed HTTP methods that may be invoked to "
            "perform operations related to the resource."
        )
    )

    permissions: list[str] = pydantic.Field(
        default_factory=list,
        description=(
            "If the request is authenticated, the list of permissions "
            "that the authenticated subject has on the resource."
        )
    )