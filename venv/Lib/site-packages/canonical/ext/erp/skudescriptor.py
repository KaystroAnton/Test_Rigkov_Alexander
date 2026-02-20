# Copyright (C) 2023-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import decimal
from typing import Any

import pydantic
from canonical import ResourceName
from canonical import Text


class SKUDescriptor(pydantic.BaseModel):
    model_config = {'populate_by_name': True}
    _resources: dict[str, ResourceName] = pydantic.PrivateAttr()

    code: str = pydantic.Field(
        default='',
        description=(
            "The code representing the stock keeping unit."
        ),
    )

    country_of_origin: str | None = pydantic.Field(
        default=None,
        alias='countryOfOrigin',
        title='Country of Origin',
        description=(
            "Country of origin of the product, if applicable."
        ),
        max_length=2
    )

    hs: str | None = pydantic.Field(
        default=None,
        title='Harmonized System (HS)',
        description=(
            "Harmonized System (HS) code of the product.\n\n"
            "The Harmonized Commodity Description and Coding System, "
            "also known as the Harmonized System (HS) of tariff "
            "nomenclature is an internationally standardized system of "
            "names and numbers to classify traded products. It came into "
            "effect in 1988 and has since been developed and maintained "
            "by the World Customs Organization (WCO) (formerly the "
            "Customs Co-operation Council), an independent "
            "intergovernmental organization based in Brussels, Belgium."
        )
    )

    product_name: Text = pydantic.Field(
        default=...,
        alias='productName',
        title='Product name',
        description=(
            "The internal display name of the product or service. May differ "
            "from what is shown to customers."
        )
    )

    ean: str | None = pydantic.Field(
        default=None,
        title='EAN',
        description=(
            "The International Article Number, (also known as European "
            "Article Number or EAN) is a standard describing a barcode "
            "symbology and numbering system used in global trade to "
            "identify a specific retail product type, in a specific "
            "packaging configuration, from a specific manufacturer. "
        ),
        max_length=13
    )

    external_resources: list[ResourceName] = pydantic.Field(
        default_factory=list,
        alias='externalResources',
        title='External references',
        description=(
            "Lists the external resources that depend on this SKU."
        )
    )

    weight: decimal.Decimal | None = pydantic.Field(
        default=None,
        title='Weight',
        description="Weight of the product in grams."
    )

    @property
    def pk(self) -> str:
        return self.code

    @property
    def resources(self) -> dict[str, ResourceName]:
        return self._resources

    def add_resource(self, name: str | ResourceName) -> None:
        if not isinstance(name, ResourceName):
            name = ResourceName(name)
        if name in self.external_resources:
            return
        self.external_resources.append(name)
        self._resources[name.service] = name

    def model_post_init(self, _: Any) -> None:
        self._resources = {x.service: x for x in self.external_resources}

    def has(self, service: str, kind: str | None = None) -> bool:
        if kind is None:
            result = service in self._resources
        else:
            result = any([
                x.service == service and x.kind == kind
                for x in self.external_resources
            ])
        return result