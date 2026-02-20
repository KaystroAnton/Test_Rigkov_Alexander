# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
import decimal
import functools
import hashlib
import struct
from typing import overload
from typing import Any
from typing import Iterable
from typing import Literal
from typing import Protocol



class IHasher(Protocol):
    def update(self, value: bytes) -> None: ...



@overload
def deephash(obj: Any, *, encode: Literal['hex']) -> str: ...


@overload
def deephash(obj: Any, *, encode: None = None) -> bytes: ...


def deephash(obj: Any, *, encode: Literal['hex'] | None = None) -> bytes | str:
    h = hashlib.sha3_256()
    hasher(obj, h)
    return h.hexdigest() if encode == 'hex' else h.digest()


@functools.singledispatch
def hasher(o: Any, h: Any) -> None:
    raise NotImplementedError(type(o).__name__)


@hasher.register
def deephash_bytes(obj: bytes, h: IHasher):
    h.update(obj)


@hasher.register
def deephash_date(obj: datetime.date, h: IHasher):
    hasher((obj.year, obj.month, obj.day), h)


@hasher.register
def deephash_datetime(obj: datetime.datetime, h: IHasher):
    hasher(obj.timestamp(), h)
    hasher(obj.tzinfo or '', h)


@hasher.register
def deephash_decimal(obj: decimal.Decimal, h: IHasher):
    h.update(str.encode(str(obj)))


@hasher.register
def deephash_dict(obj: dict, h: IHasher): # type: ignore
    key_hashes: Iterable[tuple[Any, str]] = sorted([
        (deephash(k, encode='hex'), k) for k in obj.keys() # type: ignore
    ])
    for hashed_key, key in sorted(key_hashes, key=lambda x: x[0]):
        hasher(hashed_key, h)
        hasher(obj[key], h) # type: ignore


@hasher.register
def deephash_float(obj: float, h: IHasher): # type: ignore
    hasher(struct.pack('<d', obj), h)


@hasher.register
def deephash_int(obj: int, h: IHasher): # type: ignore
    hasher(obj.to_bytes(16, 'big'), h)


def deephash_iterable(obj: Iterable[Any], h: IHasher):
    for item in obj:
        hasher(item, h)


@hasher.register
def deephash_int(obj: int, h: IHasher): # type: ignore
    hasher(obj.to_bytes(16, 'big'), h)


@hasher.register
def deephash_list(obj: list, h: IHasher): # type: ignore
    return deephash_iterable(obj, h) # type: ignore


@hasher.register
def deephash_none(obj: None, h: IHasher):
    hasher(b'', h)


@hasher.register
def deephash_set(obj: set, h: IHasher): # type: ignore
    return deephash_iterable(obj, h) # type: ignore


@hasher.register
def deephash_set(obj: tuple, h: IHasher): # type: ignore
    return deephash_iterable(obj, h) # type: ignore


@hasher.register
def deephash_string(obj: str, h: IHasher):
    hasher(str.encode(obj, 'utf-8'), h)