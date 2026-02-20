# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Union

from .authorizationrequest import AuthorizationRequest
from .authorizationcoderequest import AuthorizationCodeRequest
from .clientcredentialsrequest import ClientCredentialsRequest
from .devicecoderequest import DeviceCodeRequest
from .grantmodel import GrantModel
from .jwtbearerrequest import JWTBearerRequest
from .refreshtokenrequest import RefreshTokenRequest
from .passwordcredentialsrequest import PasswordCredentialsRequest
from .tokenexchangerequest import TokenExchangeRequest


__all__: list[str] = [
    'AuthorizationRequest',
    'AuthorizationCodeRequest',
    'ClientCredentialsRequest',
    'DeviceCodeRequest',
    'GrantModel',
    'JWTBearerRequest',
    'PasswordCredentialsRequest',
    'RefreshTokenRequest',
    'TokenExchangeRequest',
]


TokenRequestType = Union[
    AuthorizationCodeRequest,
    ClientCredentialsRequest,
    DeviceCodeRequest,
    JWTBearerRequest,
    PasswordCredentialsRequest,
    RefreshTokenRequest,
    TokenExchangeRequest
]