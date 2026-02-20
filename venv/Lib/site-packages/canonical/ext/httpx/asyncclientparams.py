# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import typing
from typing import NotRequired
from typing import TypedDict

from httpx import AsyncBaseTransport
from httpx._config import Limits
from httpx._types import AuthTypes
from httpx._types import CertTypes
from httpx._types import CookieTypes
from httpx._types import HeaderTypes
from httpx._types import ProxiesTypes
from httpx._types import ProxyTypes
from httpx._types import QueryParamTypes
from httpx._types import TimeoutTypes
from httpx._types import VerifyTypes
from httpx._types import URLTypes


class AsyncClientParams(TypedDict):
    auth: NotRequired[AuthTypes]
    params: NotRequired[QueryParamTypes]
    headers: NotRequired[HeaderTypes]
    cookies: NotRequired[CookieTypes]
    verify: NotRequired[VerifyTypes]
    cert: NotRequired[CertTypes]
    http1: NotRequired[bool]
    http2: NotRequired[bool]
    proxy: NotRequired[ProxyTypes]
    proxies: NotRequired[ProxiesTypes]
    mounts: NotRequired[
        typing.Mapping[str, NotRequired[AsyncBaseTransport]]
    ]
    timeout: NotRequired[TimeoutTypes]
    follow_redirects: NotRequired[bool]
    limits: NotRequired[Limits]
    max_redirects: NotRequired[int]
    event_hooks: NotRequired[
        typing.Mapping[str, typing.List[typing.Callable[..., typing.Any]]]
    ]
    base_url: NotRequired[URLTypes]
    transport: NotRequired[AsyncBaseTransport]
    app: NotRequired[typing.Callable[..., typing.Any]]
    trust_env: NotRequired[bool]
    default_encoding: NotRequired[typing.Union[str, typing.Callable[[bytes], str]]]