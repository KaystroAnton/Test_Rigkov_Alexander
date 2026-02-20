# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Literal
from inspect import Parameter
from inspect import Signature
from typing import Any
from typing import Callable
from typing import Union

import aorta
import pydantic

from canonical.lib.protocols import ICommand
from .default import Default


class Command(Default[Any]):
    detail = True
    exists = True
    method = 'POST'
    requires_body = True
    verb = 'issueCommand'

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.commands: list[tuple[type[ICommand], str, Callable[..., Any]]] = []

    def add(self, command: type[ICommand], verb: str, handler: Callable[..., Any]) -> None:
        self.commands.append((command, verb, handler))

    def annotate_handler(self, signature: Signature) -> Signature:
        annotation = Union[*[  # type: ignore
            self.build_command_model(c)  # type: ignore
            for c, *_ in self.commands
        ]]
        return signature.replace(
            parameters=[
                Parameter(
                    kind=Parameter.POSITIONAL_ONLY,
                    name='command',
                    annotation=annotation
                ),
                *signature.parameters.values()
            ]
        )

    def build_command_model(self, cls: type[aorta.Command]):
        attrs: dict[str, Any] = {
            'api_version': pydantic.Field(
                default=...,
                alias='apiVersion',
                title='API Version',
                description=(
                    "The `apiVersion` field defines the versioned schema of "
                    "this representation of a command."
                )
            ),
            'kind': pydantic.Field(
                default=...,
                description=(
                    "Kind is a string value representing the kind of command "
                    "that is issued."
                )
            ),
            'spec': pydantic.Field(
                default=...,
                title='Specification',
                description='Specification of the command parameters.'
            ),
            '__annotations__': {
                'api_version': Literal[f'{self.model.__meta__.api_version}'],
                'kind': Literal[f'{cls.__name__}'],
                'spec': cls
            }
        }
        return type(cls.__name__, (pydantic.BaseModel,), attrs)

    def get_endpoint_summary(self) -> str:
        return f'Issue a command'

    def get_response_description(self) -> str:
        return 'IssuedCommand object.'

    def get_path(self) -> str:
        return f'{super().get_path()}/commands'

    async def handle(self) -> None:
        raise NotImplementedError