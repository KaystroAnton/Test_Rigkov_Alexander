# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from canonical.ext.jose import JOSE
from canonical.ext.jose.models import JWS



OPAQUE_JWT = (
    "eyJhbGciOiJSUzI1NiIsImtpZCI6IjkwOWIyZmYwZmYzNjJjMTI0ZjhlMjY0NDZkYW"
    "VjZDU0NGNjZjU0ZDMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiAiY29jaGlzZUBtb2xhb"
    "m8tcGkxMW54LXN2Yy5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsICJzdWIiOiAiY29"
    "tLm1vbGFub2FwaXMuZXhpbSJ9.U0JNNnVRUTFXdEkySXlJVXBGYlgwZ2Z2eUZHMnJn"
    "Z2FoNUFpRjA0dThZTlJRVnI3UnNoZXNHZ3hUaEZGSWRSSWQ1ejBzMWMyeWIzNGJ2S1"
    "RtcHBkR0RYcEhvdC1YWUw2MjJwMXdiVlVJWWVDdG1WMDJ4LUkxZ0FMamoza09rVGR2"
    "N0t2YzNUdlEyaHBfVmVIR002a2w3bFBfSWtmTnpMZk1naGh3dWFZSGphWmhuLWZBOW"
    "g3UG00aFMydlp3cVlKR0lqRFBKSTZ5V0tSOGpqYS03YlN3REs2Wlo0cVJwRGgwWmtv"
    "M1hNV055Q0hSR2RZTm93aWtpbVZwelBfdDNQR2s2NEUzdVZCTXVfVnpWZ2JmdVo1b2"
    "tYWEQ2a2dIYTFkSkRpV2dZU1FfcllGVHhIQ2ZwRjhqR1NaQXJsM2lwOUFDVzVuVDg0"
    "MUYtSkQzakFGNGMwWWtB"
)


def test_encoding_does_not_change_signature():
    o1 = JOSE.model_validate(OPAQUE_JWT)
    o2 = JOSE.model_validate(o1.compact())
    assert isinstance(o1.root, JWS)
    assert isinstance(o2.root, JWS)
    assert o1.compact() == o2.compact()