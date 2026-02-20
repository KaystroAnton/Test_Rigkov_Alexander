# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import inspect
from typing import Any
from typing import Iterable

from canonical.utils import class_property
from canonical.utils import merge_signatures
from .protocols import IResourceAuthorizationContext
from .types import PermissionSet


class BaseAuthorizationContext(IResourceAuthorizationContext):

    @class_property
    def __signature__(cls) -> inspect.Signature:
        return merge_signatures([
            inspect.signature(cls.__init__),
            inspect.signature(cls.require)
        ])

    def __init__(self, **kwargs: Any) -> None:
        self.require(**kwargs)

    def require(self, **_: Any):
        pass

    def get_permission_name(self, api_group: str, plural: str, verb: str) -> str:
        domain = None
        service = api_group
        permission = f'{plural}.{verb}'
        if api_group == '':
            api_group = 'core'
        if api_group and api_group.find('.') != -1:
            service, domain = str.split(api_group, '.', 1)
        permission = f'{service}.{plural}.{verb}'
        if domain is not None:
            permission = f'{domain}/{service}.{plural}.{verb}'
        return permission

    def has_permissions(self, permissions: Iterable[str]) -> set[str]:
        raise NotImplementedError

    def is_authenticated(self) -> bool:
        return False

    def is_authorized(self) -> bool:
        return False

    async def has(self, permissions: str | set[str]) -> bool:
        raise NotImplementedError

    async def get_permissions(self, permissions: set[str]) -> PermissionSet:
        raise NotImplementedError

    async def setup(self):
        pass

    async def teardown(self):
        pass

    async def _setup(self):
        await self.setup()
        return self

    def __await__(self):
        return self._setup().__await__()

    async def __aenter__(self):
        await self.setup()
        return self

    async def __aexit__(
        self,
        cls: type[Exception],
        exception: Exception,
        traceback: Any
    ) -> None:
        await self.teardown()