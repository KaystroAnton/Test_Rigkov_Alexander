# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Iterable

from .mediatype import get_best_match


class MediaTypeSelector:

    def __init__(self, allow: Iterable[str]):
        self.allow = set(allow)

    def select(self, header: str | None):
        if header is None:
            return None
        return get_best_match(header, self.allow)