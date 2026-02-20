# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
import json
import secrets
import os
from typing import Any

from google.auth.credentials import Credentials
from google.cloud.iam_credentials_v1 import IAMCredentialsAsyncClient

from canonical.ext.jose.protocols import ITokenSigner


class ServiceAccountTokenSigner(ITokenSigner):
    auto_now: bool = False
    auto_jti: bool = False
    ttl: int | None = None

    def __init__(self, credential: Credentials):
        self.client = IAMCredentialsAsyncClient(credentials=credential)
        self.email = None

        # TODO: Some tricks to find out the service account email.
        email = getattr(credential, 'service_account_email', None)
        if email in {None, 'default'} and 'GOOGLE_SERVICE_ACCOUNT_EMAIL' in os.environ:
            email = os.environ['GOOGLE_SERVICE_ACCOUNT_EMAIL']
        if email in {None, 'default'}:
            raise ValueError("Unable to discover service account email.")
        self.email = email

    async def sign_claims(self, claims: Any, ttl: int | None = None) -> str:
        """Use the service account credentials to sign a JSON Web
        Token (JWT).
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        ttl = ttl or self.ttl
        if ttl is not None:
            claims['exp'] = int((now + datetime.timedelta(seconds=ttl)).timestamp())
        if self.auto_jti:
            claims['jti'] = secrets.token_urlsafe(48)
        if self.auto_now:
            claims['iat'] = claims['nbf'] = int(now.timestamp())
        claims.setdefault('iss', self.email)
        response = await self.client.sign_jwt( # type: ignore
            name=f'projects/-/serviceAccounts/{self.email}',
            payload=json.dumps(claims)
        )
        return response.signed_jwt