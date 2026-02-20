# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import decimal
from typing import Generic
from typing import TypeVar

import pydantic

from canonical import Text
from canonical import ResourceName

from .uom import UOM


K = TypeVar('K')
T = TypeVar('T')


class DocumentProduct(pydantic.BaseModel, Generic[K]):
    """Represents a product that is involved in a :term:`Document`,
    such as a request, quote, order or invoice.
    """

    description: Text = pydantic.Field(
        default=...,
        description=(
            "A description of the item, such as the product name."
        )
    )

    labels: dict[str, str] = pydantic.Field(
        default_factory=dict,
        description=(
            "Map of string keys and values that can be used to "
            "organize and categorize (scope and select) objects."
        )
    )

    key: K = pydantic.Field(
        default=...,
        description="Internally identifies the document item."
    )

    origin: ResourceName = pydantic.Field(
        default=...,
        description=(
            "A resource name specifying the origin of the item, identifying "
            "the system that produced it."
        )
    )

    quantity: decimal.Decimal = pydantic.Field(
        default=decimal.Decimal(0),
        description=(
            "The quantity of the product involved for this item."
        )
    )
    
    sku: str = pydantic.Field(
        default=...,
        description=(
            "The Stock Keeping Unit (SKU) that globally identifies "
            "the product."
        )
    )

    uom: UOM = pydantic.Field(
        default_factory=UOM.each,
        description=(
            "The unit of measurement that measures the specified "
            "`quantity`."
        )
    )

    def label(self, type: type[T], name: str) -> T:
        adapter = pydantic.TypeAdapter(type)
        return adapter.validate_python(self.labels.get(name))