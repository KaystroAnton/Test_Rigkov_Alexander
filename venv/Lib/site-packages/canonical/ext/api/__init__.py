# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from .apimodel import APIModel
from .apimodelfield import APIModelField
from .apiresource import APIResource as APIResourceModel
from .apimodelinspector import APIModelInspector
from .apirootresource import APIRootResource as APIRootResourceModel
from .apiversioned import APIVersioned
from .apiversionedmeta import APIVersionedMeta
from .clusterobjectreference import ClusterObjectReference
from .localobjectreference import LocalObjectReference
from .objectmeta import ObjectMeta
from .objectreference import ObjectReference
from .ownerreference import OwnerReference
from .refs import *
from .registry import get_meta
from .resourcespec import ResourceSpec
from .resourcestatus import ResourceStatus
from .uidreference import UIDReference


__all__: list[str] = [
    'get_meta',
    'APIModel',
    'APIModelField',
    'APIModelInspector',
    'APIResourceModel',
    'APIRootResourceModel',
    'APIVersioned',
    'APIVersionedMeta',
    'ClusterObjectReference',
    'DefaultInspector',
    'LocalObjectReference',
    'ObjectMeta',
    'ObjectReference',
    'OwnerReference',
    'ResourceSpec',
    'ResourceStatus',
    'TypedLocalObjectReference',
    'UIDReference',
]

APIResourceType = APIResourceModel[Any] | APIRootResourceModel[Any]
DefaultInspector = APIModelInspector()