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
import random
from yaql.language.engine import parameter
from yaql.language.exceptions import YaqlExecutionException


def _is_a_number(value):
    return isinstance(value, (int, long, float, complex))

@parameter('value', custom_validator=_is_a_number)
def unary_minus(value):
    return -1 * value


@parameter('value', custom_validator=_is_a_number)
def unary_plus(value):
    return value


@parameter('a', custom_validator=_is_a_number)
@parameter('b', custom_validator=_is_a_number)
def plus(a, b):
    return a + b

@parameter('a', custom_validator=_is_a_number)
@parameter('b', custom_validator=_is_a_number)
def minus(a, b):
    return a - b


@parameter('a', custom_validator=_is_a_number)
@parameter('b', custom_validator=_is_a_number)
def multiply(a, b):
    return a * b


@parameter('a', custom_validator=_is_a_number)
@parameter('b', custom_validator=_is_a_number)
def divide(a, b):
    return a / b


# comparison
def less_then(a, b):
    return a < b


def greater_or_equals(a, b):
    return a >= b


def less_or_equals(a, b):
    return a <= b


def greater_then(a, b):
    return a > b


def equals(a, b):
    return a == b


def not_equals(a, b):
    return a != b


def to_int(value):
    try:
        return int(value)
    except Exception as e:
        raise YaqlExecutionException("Unable to convert to integer", e)


def to_float(value):
    try:
        return float(value)
    except Exception as e:
        raise YaqlExecutionException("Unable to convert to float", e)


def rand():
    return random.random()


def add_to_context(context):
    # prefix unary
    context.register_function(unary_minus, 'unary_-')
    context.register_function(unary_plus, 'unary_+')

    # arithmetic actions
    context.register_function(plus, 'operator_+')
    context.register_function(minus, 'operator_-')
    context.register_function(multiply, 'operator_*')
    context.register_function(divide, 'operator_/')

    # comparison
    context.register_function(greater_then, 'operator_>')
    context.register_function(less_then, 'operator_<')
    context.register_function(greater_or_equals, 'operator_>=')
    context.register_function(less_or_equals, 'operator_<=')
    context.register_function(equals, 'operator_=')
    context.register_function(not_equals, 'operator_!=')

    #conversion
    context.register_function(to_int, 'int')
    context.register_function(to_float, 'float')

    #random
    context.register_function(rand, 'random')
