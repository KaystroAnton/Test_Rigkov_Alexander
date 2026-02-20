# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Protocol


class IRegisteredClient(Protocol):

    @property
    def id(self) -> str:
        ...

    def allows_redirect(self, uri: str | None) -> bool:
        """Return a boolean indicating if the client allows
        redirection to the given URI.
        """
        ...

    def allows_response_type(self, response_type: str) -> bool:
        """Return a boolean indicatinf if the client allows the
        given response type.
        """
        ...

    def default_redirect(self) -> str:
        """Return the default redirection URI."""
        ...