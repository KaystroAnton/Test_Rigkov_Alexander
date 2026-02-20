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

from canonical import StringType


class ConstrainedStringType(StringType):
    pattern = r'^[0-9]+$'
    min_length = 2
    max_length = 3


@pytest.mark.parametrize('v', [
    'aaa',
    '1',
    '1234'
])
def test_invalid_model(v: str):
    class Model(pydantic.BaseModel):
        value: ConstrainedStringType

    with pytest.raises(pydantic.ValidationError):
        Model.model_validate({'value': v})