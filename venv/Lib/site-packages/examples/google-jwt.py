# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio

from canonical.ext.google.params.credential import get_credential
from canonical.ext.httpx import AsyncClient
from canonical.ext.jose import JOSE
from canonical.ext.google import ServiceAccountTokenSigner
from canonical.ext.google import ServiceAccountTokenVerifier



async def main():
    signer = ServiceAccountTokenSigner(credential=await get_credential())
    async with AsyncClient() as client:
        verifier = ServiceAccountTokenVerifier(http=client)
        obj = await signer.sign_claims(foo=1, bar=2, baz=3)
        jws = JOSE.model_validate(obj)
        print("The token is valid:", await jws.verify(verifier))

if __name__ == '__main__':
    asyncio.run(main())