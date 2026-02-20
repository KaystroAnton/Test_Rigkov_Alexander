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

from canonical import HTTPResourceLocator



class Model(pydantic.BaseModel):
    url: HTTPResourceLocator


@pytest.mark.parametrize('value,exc_class', [
    ('http://www.google.com', None),
    ('https://www.google.com', None),
    ('file://www.google.com', pydantic.ValidationError),
    ('+31456', pydantic.ValidationError),
    ('a', pydantic.ValidationError),
    (1, pydantic.ValidationError)
])
def test_validate(value: str, exc_class: type[BaseException] | None):
    adapter = pydantic.TypeAdapter(HTTPResourceLocator)
    if exc_class is None:
        adapter.validate_python(value)
    else:
        with pytest.raises(exc_class):
            adapter.validate_python(value)


@pytest.mark.parametrize('value', [
    'http://www.google.com',
    'https://www.google.com',
])
def test_validate_model(value: str):
    obj = Model.model_validate({'url': value})
    assert isinstance(obj.url, HTTPResourceLocator)