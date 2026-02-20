# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from canonical.ext.fastapi import ResourceRouter
from canonical.ext.fastapi import params
from canonical.ext.fastapi import verbs

from canonical.ext.oauth.params import RedirectedState
from ..clusterclient import ClusterClient
from ..clusterprovider import ClusterProvider
from ..provider import Provider
from ..resources import AuthorizationState


__all__: list[str] = [
    'authorizationstates',
    'clusterclients',
    'clusterproviders',
    'providers',
]

authorizationstates = ResourceRouter.new(AuthorizationState)
authorizationstates.add_verb(verbs.Retrieve)
client = fastapi.APIRouter(prefix='/oauth/v2')
clusterclients = ResourceRouter.new(ClusterClient) 
clusterclients.add_verb(verbs.DefaultCreate)
clusterclients.add_verb(verbs.DefaultReplace)
clusterclients.add_verb(verbs.Retrieve, ttl=3600)
clusterproviders = ResourceRouter.new(ClusterProvider)
clusterproviders.add_verb(verbs.DefaultCreate)
providers = ResourceRouter.new(Provider)
providers.add_verb(verbs.DefaultCreate)


@clusterproviders.verb(verbs.Retrieve, authenticated=False, ttl=3600)
async def retrieve_cluster(
    verb: verbs.Retrieve[ClusterProvider],
    client: params.HTTPClient,
    obj: ClusterProvider
):
    if obj.is_discoverable():
        await obj.discover(client)
    return obj


@client.get('/callback', name='oauth2.callback')
def f(
    request: fastapi.Request,
    state: RedirectedState
):
    if not state.is_proxy() or state.is_failed():
        raise NotImplementedError
    return fastapi.responses.RedirectResponse(
        status_code=302,
        url=state.get_return_url(
            iss=f'{request.url.scheme}://{request.url.netloc}'
        )
    )
    