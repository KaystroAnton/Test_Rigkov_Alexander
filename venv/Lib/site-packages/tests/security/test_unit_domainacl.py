# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic
import pytest

from canonical.security import DomainACL


class Model(pydantic.BaseModel):
    acl: DomainACL


@pytest.mark.parametrize("values", [
    ([]),
    (["example.com"]),
    (["~example.com"]),
    (["example.com", "~example.com"]),
])
def test_bool_true(values: list[str]):
    acl = DomainACL.fromiterable(values)
    assert acl


def test_bool_false():
    acl = DomainACL.null()
    assert not acl


def test_empty_does_allow_any():
    acl = DomainACL.null()
    assert not acl
    assert acl.allows("example.com")
    

@pytest.mark.parametrize("domain,allows", [
    ("example.com", True),
    ("example.net", False),
])
def test_allows(domain: str, allows: bool):
    acl = DomainACL.fromiterable([
        "example.com",
        "~example.net"
    ])
    assert acl.allows(domain) == allows
    

@pytest.mark.parametrize("domain,allows", [
    ("example.com", True),
    ("google.com", True),
    ("microsoft.com", True),
    ("gmail.com", True),
    ("outlook.com", True),
    ("example.net", False),
])
def test_allows_all_except_denied(domain: str, allows: bool):
    acl = DomainACL.fromiterable([
        "ALL",
        "~example.net"
    ])
    assert acl.allows(domain) == allows


def test_serialize():
    acl = DomainACL.fromiterable([
        "example.com",
        "~example.net"
    ])
    assert set(acl.serialize()) == {"example.com", "~example.net"} # type: ignore


def test_serialize_null():
    acl = DomainACL.null()
    assert acl.serialize() is None


@pytest.mark.parametrize("value", [
    ([]),
    (["example.com"]),
    None
])
def test_model_validate(value: list[str] | None):
    obj = Model.model_validate({
        'acl': value
    })
    assert isinstance(obj.acl, DomainACL)


@pytest.mark.parametrize("value", [
    ([]),
    (["example.com"]),
    None
])
def test_model_validate_json(value: list[str] | None):
    obj1 = Model(acl=value).model_dump_json() # type: ignore
    obj2 = Model.model_validate_json(obj1)
    assert obj2.acl.serialize() == value


@pytest.mark.parametrize("value", [
    ([]),
    (["example.com"]),
    None
])
def test_model_init(value: list[str] | None):
    obj = Model(acl=value) # type: ignore
    assert isinstance(obj.acl, DomainACL)


@pytest.mark.parametrize("value", [
    ([]),
    (["example.com"]),
    None
])
def test_model_dump(value: list[str] | None):
    obj = Model(acl=value) # type: ignore
    assert obj.model_dump()['acl'] == value