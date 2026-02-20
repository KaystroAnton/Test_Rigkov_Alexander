# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Protocol

from canonical.protocols import ITransaction
from .idatastoreentity import IDatastoreEntity


class IDatastoreTransaction(ITransaction, Protocol):
    __module__: str = 'cbra.ext.google.types'

    def begin(self) -> None: ...
    def commit(self) -> None: ...
    def put(self, entity: IDatastoreEntity) -> None: ...
    def rollback(self) -> None: ...
    def __enter__(self): ...
    def __exit__(self, *args: Any): ...