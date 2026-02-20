# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any


RESPONSE_CONTENT_TYPE: dict[str, Any] = {
    'Content-Type': {
        'schema': {'type': 'string'},
        'required': True,
        'description': (
            "The `Content-Type` representation header is used to "
            "indicate the original media type of the resource "
            "(prior to any content encoding applied for sending)."
        )
    }
}

RESPONSE_ETAG_RESOURCE: dict[str, Any] = {
    'ETag': {
        'schema': {'type': 'string'},
        'required': True,
        'description': (
            "The `ETag` header indicates the returned version of the resource. "
            "It matches the `.metadata.resourceVersion` of the response.\n\n"
            "The `ETag` (or entity tag) HTTP response header is an identifier "
            "for a specific version of a resource. It lets caches be more "
            "efficient and save bandwidth, as the server does not need to "
            "resend a full response if the content was not changed. "
            "Additionally, etags help to prevent simultaneous updates of "
            "a resource from overwriting each other (\"mid-air collisions\")."
        )
    }
}