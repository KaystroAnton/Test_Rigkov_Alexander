# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .canonicalexception import CanonicalException


class Inconsistent(CanonicalException, LookupError):
    """An exception class that indicates that a certain resource
    is in an inconsistent state.
    """
    __module__: str = 'canonical.exceptions'

    def __init__(self, detail: str):
        self.detail = detail