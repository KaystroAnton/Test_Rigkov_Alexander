# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from canonical.lib.types import StringType


class APIVersion(StringType):
    group: str
    version: str

    def type_post_init(self):
        if self.find('/') != -1:
            self.group, self.version = str.rsplit(self, '/', maxsplit=1)
        else:
            self.group = ''
            self.version = str(self)

    def __repr__(self) -> str:
        return str(self)