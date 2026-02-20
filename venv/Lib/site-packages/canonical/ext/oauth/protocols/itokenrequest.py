# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Protocol

from canonical.ext.oauth.types import AuthenticationMethod


class ITokenRequest(Protocol):

    def identify(self, client_id: str) -> None:
        ...

    def set_client_secret(self, mode: AuthenticationMethod, secret: str) -> None:
        ...