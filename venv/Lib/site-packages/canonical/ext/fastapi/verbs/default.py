# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TypeVar

from canonical.ext.api import APIResourceType
from .base import BaseOperation


T = TypeVar('T', bound=APIResourceType)


class Default(BaseOperation[T]):

    def __init__(self, model: type[APIResourceType], **kwargs: Any):
        super().__init__(verb=self.verb, model=model, **kwargs)