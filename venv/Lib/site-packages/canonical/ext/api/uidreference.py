# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .apimodel import APIModel
from .bases import BaseReference
from .types import APIVersion


__all__: list[str] = [
    'UIDReference'
]


class UIDReference(APIModel, BaseReference):
    _namespace: str | None = pydantic.PrivateAttr(default=None)
    api_version: APIVersion
    kind: str
    uid: int

    @property
    def api_group(self) -> str:
        return self.api_version.group

    def as_name(self) -> int | str:
        return self.uid

    def get_namespace(self) -> str | None:
        return None