# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal
from typing import Union

import pydantic

from canonical import DomainName
from canonical import EmailAddress
from canonical import ResourceName
from .basesubject import BaseSubject


SubjectType = Union[
    BaseSubject[Literal['Domain'],  DomainName],
    BaseSubject[Literal['Group'],  ResourceName],
    BaseSubject[Literal['ServiceAccount'], EmailAddress | ResourceName],
    BaseSubject[Literal['User'], EmailAddress | ResourceName | Literal['allUsers'] | Literal['allAuthenticatedUsers']],
]


class Subject(pydantic.RootModel[SubjectType]):
    pass