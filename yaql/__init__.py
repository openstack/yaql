#    Copyright (c) 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import parser
import context
from yaql.functions import builtin, extended

__versioninfo__ = (0, 2, 1)
__version__ = '.'.join(map(str, __versioninfo__))


def parse(expression):
    return parser.parse(expression)


def create_context(include_extended_functions=True):
    cont = context.Context()
    builtin.add_to_context(cont)
    if include_extended_functions:
        extended.add_to_context(cont)
    return context.Context(cont)
