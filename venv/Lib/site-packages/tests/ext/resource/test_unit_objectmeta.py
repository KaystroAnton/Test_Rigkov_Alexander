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

from canonical.ext.api import APIResourceModel
from canonical.ext.api import ObjectMeta


class Order(APIResourceModel[int], group='', version='v2', plural='rs', namespaced=True):
    model_config = {'extra': 'forbid'}


def test_default_implementation_is_not_namespaced():
    assert 'namespace' not in ObjectMeta.model_fields


def test_name_is_validated():
    with pytest.raises(pydantic.ValidationError):
        Order.model_input({
            'metadata': {'namespace': 'foo', 'name': 'bar'}
        })

    Order.model_input({
        'metadata': {'namespace': 'foo', 'name': 1}
    })