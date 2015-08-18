#    Copyright (c) 2015 Mirantis, Inc.
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

from yaql.language import specs
from yaql.language import yaqltypes


@specs.parameter('left', yaqltypes.Lambda())
@specs.parameter('right', yaqltypes.Lambda())
@specs.name('#operator_and')
def and_(left, right):
    return left() and right()


@specs.parameter('left', yaqltypes.Lambda())
@specs.parameter('right', yaqltypes.Lambda())
@specs.name('#operator_or')
def or_(left, right):
    return left() or right()


@specs.parameter('arg', bool)
@specs.name('#unary_operator_not')
def not_(arg):
    return not arg


def bool_(value):
    return bool(value)


def is_boolean(value):
    return isinstance(value, bool)


@specs.parameter('right', bool)
@specs.parameter('left', bool)
@specs.name('*equal')
def eq(left, right):
    return left == right


@specs.parameter('right', bool)
@specs.parameter('left', bool)
@specs.name('*not_equal')
def neq(left, right):
    return left != right


def register(context):
    context.register_function(and_)
    context.register_function(or_)
    context.register_function(not_)
    context.register_function(bool_)
    context.register_function(is_boolean)
    context.register_function(eq)
    context.register_function(neq)
