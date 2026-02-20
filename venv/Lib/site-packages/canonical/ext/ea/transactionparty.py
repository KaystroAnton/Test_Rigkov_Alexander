# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic
from typing import cast
from typing import get_args
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Generic
from typing import Literal
from typing import MutableMapping
from typing import TypeVar

from canonical import DisplayName
from canonical import DomainName
from canonical import EmailAddress
from canonical import ResourceName
from canonical import PersonalName
from canonical import Phonenumber


DefaultKeyType = ResourceName | EmailAddress | DomainName | Phonenumber | int
C = TypeVar('C')
K = TypeVar('K')
R = TypeVar('R', bound=Any)


class BaseTransactionParty(pydantic.BaseModel, Generic[K, R]):
    """Describes a :term:`Party` that participates in
    a :term:`Transaction`.

    A :class:`TransactionParty` instance contains sufficient
    information to either retrieve or create a corresponding
    entity in an external system, such as a Customer Relationship
    Management (CRM) system.
    """
    model_config = {'populate_by_name': True}

    kind: Literal['Organization', 'NaturalPerson', 'Unspecified'] = pydantic.Field(
        default='Unspecified',
        description=(
            "Used to distinguish between B2C and B2B."
        )
    )

    key: K = pydantic.Field(
        default=...,
        description=(
            "A data element that identifier the party. May be a "
            "`ResourceName`, email address, phone number or "
            "integer identifier."
        )
    )

    transaction: ResourceName | int | None = pydantic.Field(
        default=None,
        description=(
            "Optionaly identifies the transaction. This field may be "
            "left empty if the `TransactionParty` is part of a schema "
            "from which the transaction can be inferred through other "
            "properties."
        )
    )

    party_name: PersonalName | DisplayName = pydantic.Field(
        default=...,
        alias='partyName',
        description=(
            "The name of the party. For organizations, this field is a string;"
            " for natural persons this field is a `PersonalName "
            "object."
        )
    )

    roles: set[R] = pydantic.Field(
        default_factory=set,
        description=(
            "A set indicating the roles that the participating "
            "party has in the transaction."
        ),
        min_length=1
    )

    resource_links: set[ResourceName] = pydantic.Field(
        default_factory=set,
        alias='resourceLinks',
        description=(
            "An array of strings identifying the external resources linked to "
            "the participating party, such as a record in a CRM system."
        )
    )

    email: EmailAddress | None = pydantic.Field(
        default=None,
        description=(
            "The email address of the participating party, if known."
        )
    )

    phonenumber: Phonenumber | str | None = pydantic.Field(
        default=None,
        description=(
            "The phone number of the participating party, if known."
        )
    )

    @property
    def display_name(self) -> str:
        return self.party_name.display_name

    @property
    def role(self) -> R:
        if len(self.roles) > 1:
            raise ValueError("Participating party has multiple roles.")
        return list(self.roles)[0]

    def model_post_init(self, _: Any) -> None:
        if not self.email and isinstance(self.key, EmailAddress):
            self.email = self.key
        if not self.phonenumber and isinstance(self.key, Phonenumber):
            self.phonenumber = self.key
        if not self.roles:
            raise ValueError("At least one role must be specified.")

    def has_link(self, service: str, kind: str | None = None) -> bool:
        """Return a boolean indicating if the participating party is
        linked to an external resource in the given `service`, optionally
        further specified by the `kind` parameter.
        """
        for name in self.resource_links:
            if name.service != service:
                continue
            if kind is not None and name.kind != kind:
                continue
            result = True
            break
        else:
            result = False
        return result

    def has_role(self, role_name: str) -> bool:
        """Return a boolean indicating if the party participates in
        the transaction with the given role.
        """
        if not get_args(self.model_fields['roles'].annotation) == (str,):
            raise NotImplementedError("Subclasses must override this method.")
        return role_name in cast(set[str], self.roles)

    def update_party(self, params: MutableMapping[str, Any]):
        if self.kind == 'Organization':
            params['organization_name'] = str(self.party_name.display_name)
        if self.kind == 'NaturalPerson':
            assert isinstance(self.party_name, PersonalName)
            params.update({
                'given_name': self.party_name.given_name,
                'family_name': self.party_name.family_name
            })
        if self.email:
            emails: list[Any] = params.setdefault('emails', [])
            emails.append({'value': self.email})
        if self.phonenumber:
            phonenumbers: list[Any] = params.setdefault('emails', [])
            phonenumbers.append({'value': self.phonenumber})

    async def retrieve(
        self,
        func: Callable[..., Awaitable[C]]
    ) -> C:
        """Retrieve a record from an external system."""
        return await func(self)


class TransactionParty(BaseTransactionParty[DefaultKeyType, str]):
    model_config = {'populate_by_name': True}