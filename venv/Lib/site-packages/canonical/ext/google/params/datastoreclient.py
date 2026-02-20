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
from google.cloud import datastore

from .credential import Credential
from .datastorenamespace import DatastoreNamespace
from .datastoreproject import DatastoreProject


__all__: list[str] = ['DatastoreClient']


async def get(
    credential: Credential,
    project: DatastoreProject,
    namespace: DatastoreNamespace    
) -> datastore.Client:
    return datastore.Client(
        credentials=credential,
        project=project,
        namespace=namespace
    )


DatastoreClient: TypeAlias = Annotated[datastore.Client, fastapi.Depends(get)]