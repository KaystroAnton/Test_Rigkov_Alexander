# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Annotated
from typing import TypeAlias

import fastapi

from ..basedatastorestorage import BaseDatastoreStorage
from .datastoreclient import DatastoreClient


__all__: list[str] = ['Datastore']


async def get(
    client: DatastoreClient
):
    return BaseDatastoreStorage(client=client)


Datastore: TypeAlias = Annotated[BaseDatastoreStorage, fastapi.Depends(get)]