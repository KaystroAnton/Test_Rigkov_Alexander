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

from canonical import Phonenumber



class Model(pydantic.BaseModel):
    phonenumber: Phonenumber


@pytest.mark.parametrize('value,exc_class', [
    ('+31612345678', None),
    ('+31456', pydantic.ValidationError),
    ('a', pydantic.ValidationError),
    (1, pydantic.ValidationError)
])
def test_validate(value: str, exc_class: type[BaseException] | None):
    adapter = pydantic.TypeAdapter(Phonenumber)
    if exc_class is None:
        adapter.validate_python(value)
    else:
        with pytest.raises(exc_class):
            adapter.validate_python(value)


@pytest.mark.parametrize('value', [
    '+31612345678'
])
def test_validate_model(value: str):
    obj = Model.model_validate({'phonenumber': value})
    assert isinstance(obj.phonenumber, Phonenumber)