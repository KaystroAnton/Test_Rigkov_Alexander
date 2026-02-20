# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import copy
import os

import jinja2
import pydantic
import yaml


class ConfigFileModel(pydantic.BaseModel):

    @classmethod
    def open(cls, fn: str):
        with open(fn) as f:
            t = jinja2.Template(
                f.read(),
                variable_start_string='${',
                variable_end_string='}',
                undefined=jinja2.StrictUndefined
            )
        data = yaml.safe_load(t.render(env=copy.copy(os.environ))) # type: ignore
        return cls.model_validate(data)