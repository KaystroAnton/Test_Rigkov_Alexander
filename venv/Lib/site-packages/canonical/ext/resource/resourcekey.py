# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Annotated
from typing_extensions import Doc

from canonical.ext.api import ObjectReference
from canonical.ext.api import LocalObjectReference



ResourceUntypedKey = Annotated[
    LocalObjectReference,
    Doc(
        "An identifier for a resource from which the type can not be inferred, "
        "such as an int or a string."
    )
]

ResourceKey = Annotated[
    ObjectReference | ResourceUntypedKey,
    Doc(
        "An identifier for a resource."
    )
]


