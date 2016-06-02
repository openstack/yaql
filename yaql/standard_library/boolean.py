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
"""
Whenever an expression is used in the context of boolean operations, the
following values are interpreted as false: ``false``, ``null``, numeric zero of
any type, empty strings, empty dict, empty list, empty set, zero timespan.
All other values are interpreted as true.
"""


from yaql.language import specs
from yaql.language import yaqltypes


@specs.parameter('left', yaqltypes.Lambda())
@specs.parameter('right', yaqltypes.Lambda())
@specs.name('#operator_and')
def and_(left, right):
    """:yaql:operator and

    Returns left operand if it evaluates to false. Otherwise evaluates right
    operand and returns it.

    :signature: left and right
    :arg left: left operand
    :argType left: any
    :arg right: right operand
    :argType right: any
    :returnType: any (left or right operand types)

    .. code::

        yaql> 1 and 0
        0
        yaql> 1 and 2
        2
        yaql> [] and 1
        []
    """
    return left() and right()


@specs.parameter('left', yaqltypes.Lambda())
@specs.parameter('right', yaqltypes.Lambda())
@specs.name('#operator_or')
def or_(left, right):
    """:yaql:operator or

    Returns left operand if it evaluates to true. Otherwise evaluates right
    operand and returns it.

    :signature: left or right
    :arg left: left operand
    :argType left: any
    :arg right: right operand
    :argType right: any
    :returnType: any (left or right operand types)

    .. code::

        yaql> 1 or 0
        1
        yaql> 1 or 2
        1
        yaql> [] or 1
        1
    """
    return left() or right()


@specs.name('#unary_operator_not')
def not_(arg):
    """:yaql:operator not

    Returns true if arg evaluates to false. Otherwise returns false.

    :signature: not arg
    :arg arg: value to be converted
    :argType arg: any
    :returnType: boolean

    .. code::

        yaql> not true
        false
        yaql> not {}
        true
        yaql> not [1]
        false
    """
    return not arg


def bool_(value):
    """:yaql:bool

    Returns true or false after value type conversion to boolean.
    Function returns false if value is 0, false, empty list, empty dictionary,
    empty string, empty set, and timespan(). All other values are considered
    to be true.

    :signature: bool(value)
    :arg value: value to be converted
    :argType value: any
    :returnType: boolean

    .. code::

        yaql> bool(1)
        true
        yaql> bool([])
        false
    """
    return bool(value)


def is_boolean(value):
    """:yaql:isBoolean

    Returns true if value is boolean, otherwise false.

    :signature: isBoolean(value)
    :arg value: value to check
    :argType value: any
    :returnType: boolean

    .. code::

        yaql> isBoolean(false)
        true
        yaql> isBoolean(0)
        false
    """
    return isinstance(value, bool)


def register(context):
    context.register_function(and_)
    context.register_function(or_)
    context.register_function(not_)
    context.register_function(bool_)
    context.register_function(is_boolean)
