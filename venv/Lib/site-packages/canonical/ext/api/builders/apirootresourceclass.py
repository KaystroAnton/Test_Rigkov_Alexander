# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Generic
from typing import TypeVar
from typing import Union
from typing import TYPE_CHECKING

from canonical.exceptions import ProgrammingError
from ..bases import BaseResource
from ..bases import BaseRootResource
from .rootmodelclass import RootModelBuilder
from .rootmodeldescriptor import RootModelDescriptor
if TYPE_CHECKING:
    from ..apirootresource import APIRootResource

T = TypeVar('T', bound='APIRootResource[Any]')


class APIRootResourceClassBuilder(RootModelBuilder[T], Generic[T]):

    def setup(self, model: type[T], **kwargs: Any):
        super().setup(model, **kwargs)
        self.meta = model.__meta__
        model.__namespaced__ = bool(kwargs.get('namespaced'))

        # Check if all models in the root are
        # implementations of BaseResource.
        for child in self.children:
            if not issubclass(child, BaseResource):
                raise ProgrammingError(
                    "Child classes must inherit from BaseResource."
                )

    def build_create_model(self):
        union = Union[*[x.__create_model__ for x in self.children]] # type: ignore
        return type(self.model.__name__, (BaseRootResource[union],), {
            'model_config': {
                **self.model.model_config,
                'ignored_types': (RootModelDescriptor,)
            },
            'api_version': property(lambda self: self.root.api_version),
            'kind': property(lambda self: self.root.kind),
            'metadata': property(lambda self: self.root.metadata),
            #'replacable': property(lambda self: self.root.replacable),
        })