# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Generic
from typing import TypeVar

from canonical.ext.api import APIModelField
from canonical.ext.api import TypedLocalObjectReference
from .namespacespec import NamespaceSpec


RefType = TypeVar('RefType', bound=TypedLocalObjectReference)


class HierarchicalNamespaceSpec(NamespaceSpec, Generic[RefType]):
    parent_ref: RefType = APIModelField(
        default=None,
        alias='parent',
        description=(
            "An optional reference to a parent Resource.\n\nSupported parent "
            "types include `organization` and `folder`. Once set, the parent "
            "cannot be cleared. The parent can be set on creation or "
            "using the `projects.update` method; the end user must "
            "have the `projects.create` permission on the parent."
        ),
        when={'create', 'store', 'view'}
    )