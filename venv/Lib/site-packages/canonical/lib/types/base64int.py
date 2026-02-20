# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import binascii

from .base64type import Base64Type


__all__: list[str] = [
    'Base64Int'
]


class Base64Int(int, Base64Type[int]):
    endianness: str = 'big'

    @classmethod
    def b64input(cls, value: bytes) -> int:
        return int(binascii.b2a_hex(value), 16)

    @classmethod
    def b64output(cls, value: int) -> bytes:
        return int.to_bytes(value, (value.bit_length() + 7) // 8, 'big')