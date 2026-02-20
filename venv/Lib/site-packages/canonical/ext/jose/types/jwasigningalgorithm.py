# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import enum


class JWASigningAlgorithm(str, enum.Enum):
    hs256 = 'HS256'
    hs384 = 'HS384'
    hs512 = 'HS512'
    rs256 = 'RS256'
    rs384 = 'RS384'
    rs512 = 'RS512'
    es256 = 'ES256'
    es384 = 'ES384'
    es512 = 'ES512'
    eddsa = 'EdDSA'