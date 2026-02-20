# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pytest
import pydantic

from canonical.ext.api import APIModel



class ChildModel(APIModel):
    taz: int


class Model(APIModel):
    model_config = {'extra': 'forbid'}

    foo: int = pydantic.Field(...)
    bar: int = pydantic.Field(..., frozen=True)
    baz: ChildModel | None


class PolyModel(APIModel):
    foo: int


class InvalidModel(APIModel):
    foo: str


def test_replace():
    ours = Model(foo=1, bar=1, baz=ChildModel(taz=3))
    theirs = Model(foo=2, bar=1, baz=ChildModel(taz=2))
    ours.replace(theirs)
    assert ours.foo == theirs.foo
    assert ours.baz == theirs.baz


def test_replace_poly():
    ours = Model(foo=1, bar=1, baz=ChildModel(taz=3))
    theirs = PolyModel(foo=2)
    ours.replace(theirs)
    assert ours.foo == theirs.foo


def test_replace_invalid():
    ours = Model(foo=1, bar=1, baz=ChildModel(taz=3))
    theirs = InvalidModel(foo='aaa')
    with pytest.raises(pydantic.ValidationError):
        ours.replace(theirs)


def test_can_not_replace_frozen_fields():
    ours = Model(foo=1, bar=1, baz=None)
    theirs = Model(foo=2, bar=2, baz=None)
    ours.replace(theirs)
    assert ours.foo == theirs.foo
    assert ours.bar != theirs.bar
