# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from __future__ import annotations
import re
import types
from typing import cast
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import TypeVar

import pydantic

from .domainname import DomainName
from .stringtype import StringType


T = TypeVar('T', bound='ResourceName')
M = TypeVar('M', bound=Any)


class ResourceName(StringType):
    Typed: ClassVar[type['TypedResourceName[Any]']]
    model: Any
    relname: str
    service: DomainName
    patterns = [re.compile(r'//.*')]

    @property
    def id(self) -> str:
        return str.split(self, '/')[-1]

    @property
    def kind(self) -> str:
        return str.split(self.relname, '/')[0]

    @property
    def scalar(self) -> str:
        return self.id

    @classmethod
    def null(cls: type[T]) -> T: # pragma: no cover
        """Return an instance that represents an unassigned
        resource name.
        """
        return cls('//cochise.io/_/null')

    @classmethod
    def typed(cls, model: type[M]) -> TypedResourceName[M]:
        new_class =  types.new_class(
            name=f'{model.__name__}ResourceName',
            bases=(cls,),
            kwds={'model': model}
        )
        return cast(TypedResourceName[M], new_class)

    def __new__(cls: type[T], object: str) -> T:
        self = super().__new__(cls, object) # type: ignore
        if not str.startswith(object, '//'):
            raise ValueError("A resource name must start with slashes.")
        service, _, relname = str.partition(object[2:], '/')
        if not relname:
            raise ValueError("a valid ResourceName contains a relative name.")
        adapter = pydantic.TypeAdapter(DomainName)
        self.relname = relname
        self.service = adapter.validate_python(service)
        return cast(T, self)

    def __init_subclass__(cls, model: type[Any]) -> None:
        super().__init_subclass__()
        cls.model = model

    @classmethod
    def validate(cls, v: str, _: Any = None) -> str:
        return cls(v)


class TypedResourceName(ResourceName, Generic[M], model=pydantic.BaseModel):
    model: type[M]


ResourceName.Typed = TypedResourceName