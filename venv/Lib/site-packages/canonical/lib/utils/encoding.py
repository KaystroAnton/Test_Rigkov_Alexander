# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import base64
import binascii
import json
from typing import Any
from typing import TypeVar

import pydantic


T = TypeVar('T')


def bytes_to_number(value: bytes) -> int: # pragma: no cover
    return int(binascii.b2a_hex(value), 16)


def b64decode(buf: bytes | str, decoder: type[T] = bytes) -> T:
    """Decode the given byte-sequence or string."""
    adapter = pydantic.TypeAdapter(decoder)
    if isinstance(buf, str):
        buf = buf.encode("ascii")
    rem = len(buf) % 4
    if rem > 0:
        buf += b"=" * (4 - rem)
    return adapter.validate_python(base64.urlsafe_b64decode(buf))


def b64decode_int(value: bytes | str) -> int:
    return bytes_to_number(b64decode(value))


def b64decode_json(
    buf: bytes | str,
    encoding: str = 'utf-8',
    require: type[list[Any]] | type[dict[str, Any]] | None = None
) -> dict[str, Any] | list[Any]:
    """Deserialize a Base64-encoded string or byte-sequence as JSON."""
    result = json.loads(bytes.decode(b64decode(buf), encoding))
    if not isinstance(result, (require,) if require else (dict, list)): # pragma: no cover
        raise ValueError 
    return result


def b64encode_int(
    value: int,
    encoder: type[T] = bytes
) -> T: # pragma: no cover
    return b64encode(int.to_bytes(value, (value.bit_length() + 7) // 8, 'big'), encoder=encoder)


def b64encode_json(
    obj: dict[str, Any] | list[Any],
    encoder: type[T] = bytes
) -> T:
    """Encode the given dictionary as JSON and return the Base64-encoded
    byte-sequence.
    """
    return b64encode(json.dumps(obj, sort_keys=True), 'utf-8', encoder=encoder)


def b64encode(
    buf: bytes | str,
    encoding: str = 'utf-8',
    encoder: type[T] = bytes
) -> T:
    """Encode the given string or byte-sequence using the specified
    encoding.
    """
    adapter = pydantic.TypeAdapter(encoder)
    if isinstance(buf, str):
        buf = str.encode(buf, encoding=encoding)
    value = base64.urlsafe_b64encode(buf).replace(b"=", b"")
    return adapter.validate_python(value)