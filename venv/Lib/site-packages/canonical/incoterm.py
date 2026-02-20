# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import enum
from typing import Literal

import pydantic


__all__: list[str] = [
    'Incoterm',
    'IncotermEnum',
    'IncotermLiteral'
]


class Incoterm(pydantic.BaseModel):
    version: int = pydantic.Field(
        default=2020
    )

    term: 'IncotermLiteral' = pydantic.Field(
        default=...
    )


class IncotermEnum(str, enum.Enum):
    EXW = 'EXW'
    FCA = 'FCA'
    FAS = 'FAS'
    FOB = 'FOB'
    CPT = 'CPT'
    CIP = 'CIP'
    CFR = 'CFR'
    CIF = 'CIF'
    DAP = 'DAP'
    DPU = 'DPU'
    DDP = 'DDP'


IncotermLiteral = Literal[
    'EXW',
    'FCA',
    'FAS',
    'FOB',
    'CPT',
    'CIP',
    'CFR',
    'CIF',
    'DAP',
    'DPU',
    'DDP',
]


Incoterm.model_rebuild()