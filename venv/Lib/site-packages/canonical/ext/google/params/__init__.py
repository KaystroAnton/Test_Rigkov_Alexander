# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from .credential import Credential as GoogleCredential
from .datastore import Datastore
from .datastoreclient import DatastoreClient


__all__: list[str] = [
    'Datastore',
    'DatastoreClient',
    'GoogleCredential',
    'GoogleDatastore',
]


def GoogleDatastore(
    namespace: str | None = None
):
    def f(request: fastapi.Request):
        setattr(request.state, 'google_datastore_namespace', namespace)

    return fastapi.Depends(f)