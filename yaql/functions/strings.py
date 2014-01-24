#    Copyright (c) 2014 Mirantis, Inc.
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

import types
from yaql.language.engine import parameter


@parameter('a', arg_type=types.StringTypes)
@parameter('b', arg_type=types.StringTypes)
def string_concatenation(a, b):
    return a + b

@parameter('self', arg_type=types.StringTypes, is_self=True)
def as_list(self):
    return list(self)


def to_string(self):
    return str(self)

def _to_string_func(data):
    return to_string(data)


def add_to_context(context):
    context.register_function(string_concatenation, 'operator_+')
    context.register_function(as_list, 'asList')
    context.register_function(to_string)
    context.register_function(_to_string_func, 'string')
