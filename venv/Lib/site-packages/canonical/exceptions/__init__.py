# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .canonicalexception import CanonicalException
from .duplicate import Duplicate
from .doesnotexist import DoesNotExist
from .immutable import Immutable
from .inconsistent import Inconsistent
from .multipleobjectsreturned import MultipleObjectsReturned
from .programmingerror import ProgrammingError
from .referentdoesnotexist import ReferentDoesNotExist
from .stale import Stale


__all__: list[str] = [
    'CanonicalException',
    'Duplicate',
    'DoesNotExist',
    'Immutable',
    'Inconsistent',
    'MultipleObjectsReturned',
    'ProgrammingError',
    'ReferentDoesNotExist',
    'Stale',
]