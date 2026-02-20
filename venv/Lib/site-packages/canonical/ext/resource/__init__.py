# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .apidescriptor import APIDescriptor
from .apigroupversionlist import APIGroupVersionList
from .apiresource import APIResource as APIResourceModel
from .apiresourcelist import APIResource
from .apiresourcelist import APIResourceList
from .conditiontype import ConditionType
from .error import Error
from .iresourcequery import IResourceQuery
from .iresourcerepository import IResourceRepository
from .listbase import ListBase
from .localreference import LocalReference
from .namespacedobjectmeta import NamespacedObjectMeta
from .objectmeta import ObjectMeta
from .primarykey import PrimaryKey
from .resource import M as ObjectMetaType
from .resource import Resource
from .resourceinspector import ResourceInspector
from .resourcemeta import ResourceMeta
from .resourceserverlist import ResourceServerList
from .resourcespec import ResourceSpec
from .resourcestatus import ResourceStatus
from .rootresource import ResourceType
from .rootresource import ResourceTypeVar
from .rootresource import RootResource
from .statefulresource import StatefulResource
from .transientmeta import TransientMeta

# Public interface
from canonical.ext.api import LocalObjectReference
from canonical.ext.api import ObjectReference
from .apiversioned import APIVersioned
from .basereference import BaseReference
from .baseresourcerepository import BaseResourceRepository
from .resourcekey import ResourceKey
from .ownerreference import OwnerReference
from .typedobjectreference import TypedObjectReference



__all__: list[str] = [
    'APIDescriptor',
    'APIGroupVersionList',
    'APIResource',
    'APIResourceList',
    'APIVersioned',
    'BaseReference',
    'BaseResourceRepository',
    'ConditionType',
    'Error',
    'Inspectable',
    'IResourceQuery',
    'IResourceRepository',
    'ListBase',
    'LocalObjectReference',
    'LocalReference',
    'Namespace',
    'NamespacedObjectMeta',
    'ObjectMeta',
    'ObjectMetaType',
    'ObjectReference',
    'OwnerReference',
    'PrimaryKey',
    'Resource',
    'ResourceInspector',
    'ResourceKey',
    'ResourceMeta',
    'ResourceServerList',
    'ResourceSpec',
    'ResourceStatus',
    'ResourceType',
    'ResourceTypeVar',
    'RootResource',
    'StatefulResource',
    'TransientMeta',
    'TypedObjectReference',
]