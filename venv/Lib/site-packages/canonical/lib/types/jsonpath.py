# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from collections import abc
from typing import Any

from canonical.lib.utils import jsonpath
from .stringtype import StringType


class JSONPath(StringType):

    @classmethod
    def validate(cls, v: str, _: Any = None):
        if not str.startswith(v, '/'):
            raise ValueError("A JSON path must start with a slash.")
        return cls(v)

    def get(self, mapping: abc.Mapping[str, Any]) -> Any:
        try:
            value = jsonpath(mapping, self)
        except (KeyError, TypeError):
            value = None
        return value