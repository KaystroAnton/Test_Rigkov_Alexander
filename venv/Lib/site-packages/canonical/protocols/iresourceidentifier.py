# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Generic
from typing import Protocol
from typing import TypeVar

from .ityped import ITyped


D = TypeVar('D', covariant=True)
T = TypeVar('T', covariant=True)


class IResourceIdentifier(ITyped[T], Protocol, Generic[D, T]):
    """Identifies a resource, for example the primary key of a tuple
    in a relational database, or a URI pointing to a document.
    """
    __module__: str = 'canonical.protocols'