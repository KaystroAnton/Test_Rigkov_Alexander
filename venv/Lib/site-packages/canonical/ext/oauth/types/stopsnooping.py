# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .useragentexception import UserAgentException


class StopSnooping(UserAgentException):
    __module__: str = 'canonical.ext.oauth.types'
    page_heading = "Security incident"
    page_title = "Stop snooping"
    status_code: int = 403
    template_name: str = 'oauth/security/snooping.html.j2'