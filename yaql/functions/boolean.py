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
from yaql.language.exceptions import YaqlExecutionException


@parameter('a', arg_type=types.BooleanType)
@parameter('b', arg_type=types.BooleanType)
def _and(a, b):
    return a and b

@parameter('a', arg_type=types.BooleanType)
@parameter('b', arg_type=types.BooleanType)
def _or(a, b):
    return a or b

@parameter('data', arg_type=types.BooleanType)
def _not(data):
    return not data


def to_bool(value):
    try:
        return bool(value)
    except Exception as e:
        raise YaqlExecutionException("Unable to convert to boolean", e)


def add_to_context(context):
    context.register_function(_and, 'operator_and')
    context.register_function(_or, 'operator_or')
    context.register_function(_not, 'unary_not')
    context.register_function(_not, 'unary_!')
    context.register_function(to_bool, 'bool')
