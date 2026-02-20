# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import urllib.parse
from collections import abc
from typing import cast
from typing import Any

import pydantic


class FormDataMixin:
    model_dump = pydantic.BaseModel.model_dump

    def encode_form(self, name: str, value: Any, encoding: str) -> list[tuple[str, str]]:
        # TODO: Not very elegant, but covers most use cases.
        params: list[tuple[str, str]] = []
        if isinstance(value, abc.Mapping):
            raise ValueError("Can not dump dictionary to url encoded.")
        if isinstance(value, (str, bytes)):
            if isinstance(value, bytes):
                value = bytes.decode(value, encoding)
            params.append((name, value))
        elif isinstance(value, abc.Collection):
            value = cast(list[Any], value)
            assert isinstance(value, (list, set)), repr(value)
            for item in cast(list[Any], value):
                params.extend(self.encode_form(name, item, encoding))
        else:
            params.append((name, str(value)))
        return params

    def model_dump_urlencoded(self, encoding: str = 'utf-8', mode: str | None = None):
        if mode not in {None, 'query'}:
            raise NotImplementedError
        params: list[tuple[str, str]] = []
        data: dict[str, Any] = self.model_dump(mode='json', exclude_none=True)
        for name, value in data.items():
            params.extend(self.encode_form(name, value, encoding))
        return urllib.parse.urlencode(params, doseq=True)