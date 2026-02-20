# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
from typing import Annotated
from typing import Any
from typing import TYPE_CHECKING
from typing import Union
from typing_extensions import Doc

if TYPE_CHECKING:
    from canonical.ext.api import *


APIResourceType = Annotated[
    Union['APIResourceModel[Any]', 'APIRootResourceModel[Any]'],
    Doc("Versioned resource type.")
]

Reference = Annotated[
    Union['LocalObjectReference', 'ObjectReference', 'OwnerReference', 'UIDReference'],
    Doc("Reference type to an object.")
]