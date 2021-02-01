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
The Math module describes implemented math operations on numbers.
"""
import random

from yaql.language import specs
from yaql.language import yaqltypes


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_+')
def binary_plus(left, right):
    """:yaql:operator +

    Returns the sum of left and right operands.

    :signature: left + right
    :arg left: left operand
    :argType left: number
    :arg right: right operand
    :argType right: number
    :returnType: number

    .. code::

        yaql> 3 + 2
        5
    """
    return left + right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_-')
def binary_minus(left, right):
    """:yaql:operator -

    Returns the difference between left and right.

    :signature: left - right
    :arg left: left operand
    :argType left: number
    :arg right: right operand
    :argType right: number
    :returnType: number

    .. code::

        yaql> 3 - 2
        1
    """
    return left - right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_*')
def multiplication(left, right):
    """:yaql:operator *

    Returns left multiplied by right.

    :signature: left * right
    :arg left: left operand
    :argType left: number
    :arg right: right operand
    :argType right: number
    :returnType: number

    .. code::

        yaql> 3 * 2.5
        7.5
    """
    return left * right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_/')
def division(left, right):
    """:yaql:operator /

    Returns left divided by right.

    :signature: left / right
    :arg left: left operand
    :argType left: number
    :arg right: right operand
    :argType right: number
    :returnType: number

    .. code::

        yaql> 3 / 2
        1
        yaql> 3.0 / 2
        1.5
    """
    if isinstance(left, int) and isinstance(right, int):
        return left // right
    return left / right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_mod')
def modulo(left, right):
    """:yaql:operator mod

    Returns left modulo right.

    :signature: left mod right
    :arg left: left operand
    :argType left: number
    :arg right: right operand
    :argType right: number
    :returnType: number

    .. code::

        yaql> 3 mod 2
        1
    """
    return left % right


@specs.parameter('op', yaqltypes.Number())
@specs.name('#unary_operator_+')
def unary_plus(op):
    """:yaql:operator unary +

    Returns +op.

    :signature: +op
    :arg op: operand
    :argType op: number
    :returnType: number

    .. code::

        yaql> +2
        2
    """
    return +op


@specs.parameter('op', yaqltypes.Number())
@specs.name('#unary_operator_-')
def unary_minus(op):
    """:yaql:operator unary -

    Returns -op.

    :signature: -op
    :arg op: operand
    :argType op: number
    :returnType: number

    .. code::

        yaql> -2
        -2
    """
    return -op


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_>')
def gt(left, right):
    """:yaql:operator >

    Returns true if left is strictly greater than right, false otherwise.

    :signature: left > right
    :arg left: left operand
    :argType left: number
    :arg right: right operand
    :argType left: number
    :returnType: boolean

    .. code::

        yaql> 3 > 2
        true
    """
    return left > right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_>=')
def gte(left, right):
    """:yaql:operator >=

    Returns true if left is greater or equal to right, false otherwise.

    :signature: left >= right
    :arg left: left operand
    :argType left: number
    :arg right: right operand
    :argType left: number
    :returnType: boolean

    .. code::

        yaql> 3 >= 3
        true
    """
    return left >= right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_<')
def lt(left, right):
    """:yaql:operator <

    Returns true if left is strictly less than right, false otherwise.

    :signature: left < right
    :arg left: left operand
    :argType left: number
    :arg right: right operand
    :argType left: number
    :returnType: boolean

    .. code::

        yaql> 3 < 2
        false
    """
    return left < right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_<=')
def lte(left, right):
    """:yaql:operator <=

    Returns true if left is less or equal to right, false otherwise.

    :signature: left <= right
    :arg left: left operand
    :argType left: number
    :arg right: right operand
    :argType left: number
    :returnType: boolean

    .. code::

        yaql> 3 <= 3
        true
    """
    return left <= right


@specs.parameter('op', yaqltypes.Number())
def abs_(op):
    """:yaql:abs

    Returns the absolute value of a number.

    :signature: abs(op)
    :arg op: input value
    :argType op: number
    :returnType: number

    .. code::

        yaql> abs(-2)
        2
    """
    return abs(op)


def int_(value):
    """:yaql:int

    Returns an integer built from number, string or null value.

    :signature: int(value)
    :arg value: input value
    :argType value: number, string or null
    :returnType: integer

    .. code::

        yaql> int("2")
        2
        yaql> int(12.999)
        12
        yaql> int(null)
        0
    """
    if value is None:
        return 0
    return int(value)


def float_(value):
    """:yaql:float

    Returns a floating number built from number, string or null value.

    :signature: float(value)
    :arg value: input value
    :argType value: number, string or null
    :returnType: float

    .. code::

        yaql> float("2.2")
        2.2
        yaql> float(12)
        12.0
        yaql> float(null)
        0.0
    """
    if value is None:
        return 0.0
    return float(value)


def random_():
    """:yaql:random

    Returns the next random floating number from [0.0, 1.0).

    :signature: random()
    :returnType: float

    .. code::

        yaql> random()
        0.6039529924951869
    """
    return random.random()


def random__(from_, to_):
    """:yaql:random

    Returns the next random integer from [a, b].

    :signature: random(from, to)
    :arg from: left value for generating random number
    :argType from: integer
    :arg to: right value for generating random number
    :argType to: integer
    :returnType: integer

    .. code::

        yaql> random(1, 2)
        2
        yaql> random(1, 2)
        1
    """
    return random.randint(from_, to_)


@specs.parameter('left', int)
@specs.parameter('right', int)
def bitwise_and(left, right):
    """:yaql:bitwiseAnd

    Returns applied "bitwise and" to left and right integers.
    Each bit of the output is 1 if the corresponding bit of left AND right
    is 1, otherwise 0.

    :signature: bitwiseAnd(left, right)
    :arg left: left value
    :argType left: integer
    :arg right: right value
    :argType right: integer
    :returnType: integer

    .. code::

        yaql> bitwiseAnd(6, 12)
        4
    """
    return left & right


@specs.parameter('left', int)
@specs.parameter('right', int)
def bitwise_or(left, right):
    """:yaql:bitwiseOr

    Returns applied "bitwise or" to left and right numbers.
    Each bit of the output is 1 if the corresponding bit of left OR right
    is 1, otherwise 0.

    :signature: bitwiseOr(left, right)
    :arg left: left value
    :argType left: integer
    :arg right: right value
    :argType right: integer
    :returnType: integer

    .. code::

        yaql> bitwiseOr(6, 12)
        14
    """
    return left | right


@specs.parameter('left', int)
@specs.parameter('right', int)
def bitwise_xor(left, right):
    """:yaql:bitwiseXor

    Returns applied "bitwise exclusive or" to left and right numbers.
    Each bit of the output is equal to the sum of corresponding left and right
    bits mod 2.

    :signature: bitwiseXor(left, right)
    :arg left: left value
    :argType left: integer
    :arg right: right value
    :argType right: integer
    :returnType: integer

    .. code::

        yaql> bitwiseXor(6, 12)
        10
    """
    return left ^ right


@specs.parameter('arg', int)
def bitwise_not(arg):
    """:yaql:bitwiseNot

    Returns an integer where each bit is a reversed corresponding bit of arg.

    :signature: bitwiseNot(arg)
    :arg arg: input value
    :argType arg: integer
    :returnType: integer

    .. code::

        yaql> bitwiseNot(6)
        -7
    """
    return ~arg


@specs.parameter('value', int)
@specs.parameter('bits_number', int)
def shift_bits_right(value, bits_number):
    """:yaql:shiftBitsRight

    Shifts the bits of value right by the number of bits bitsNumber.

    :signature: shiftBitsRight(value, bitsNumber)
    :arg value: given value
    :argType value: integer
    :arg bitsNumber: number of bits
    :argType right: integer
    :returnType: integer

    .. code::

        yaql> shiftBitsRight(8, 2)
        2
    """
    return value >> bits_number


@specs.parameter('value', int)
@specs.parameter('bits_number', int)
def shift_bits_left(value, bits_number):
    """:yaql:shiftBitsLeft

    Shifts the bits of value left by the number of bits bitsNumber.

    :signature: shiftBitsLeft(value, bitsNumber)
    :arg value: given value
    :argType value: integer
    :arg bitsNumber: number of bits
    :argType right: integer
    :returnType: integer

    .. code::

        yaql> shiftBitsLeft(8, 2)
        32
    """
    return value << bits_number


@specs.parameter('a', nullable=True)
@specs.parameter('b', nullable=True)
@specs.inject('operator', yaqltypes.Delegate('#operator_>'))
def max_(a, b, operator):
    """:yaql:max

    Returns max from a and b.

    :signature: max(a, b)
    :arg a: input value
    :argType a: number
    :arg b: input value
    :argType b: number
    :returnType: number

    .. code::

        yaql> max(8, 2)
        8
    """
    if operator(b, a):
        return b
    return a


@specs.inject('operator', yaqltypes.Delegate('#operator_>'))
def min_(a, b, operator):
    """:yaql:min

    Returns min from a and b.

    :signature: min(a, b)
    :arg a: input value
    :argType a: number
    :arg b: input value
    :argType b: number
    :returnType: number

    .. code::

        yaql> min(8, 2)
        2
    """
    if operator(b, a):
        return a
    return b


@specs.parameter('a', yaqltypes.Number())
@specs.parameter('b', yaqltypes.Number())
@specs.parameter('c', yaqltypes.Number(nullable=True))
def pow_(a, b, c=None):
    """:yaql:pow

    Returns a to the power b modulo c.

    :signature: pow(a, b, c => null)
    :arg a: input value
    :argType a: number
    :arg b: power
    :argType b: number
    :arg c: modulo. null by default, which means no modulo is done after power.
    :argType c: integer
    :returnType: number

    .. code::

        yaql> pow(3, 2)
        9
        yaql> pow(3, 2, 5)
        4
    """
    return pow(a, b, c)


@specs.parameter('num', yaqltypes.Number())
def sign(num):
    """:yaql:sign

    Returns 1 if num > 0; 0 if num = 0; -1 if num < 0.

    :signature: sign(num)
    :arg num: input value
    :argType num: number
    :returnType: integer (-1, 0 or 1)

    .. code::

        yaql> sign(2)
        1
    """
    if num > 0:
        return 1
    elif num < 0:
        return -1
    return 0


@specs.parameter('number', yaqltypes.Number())
@specs.parameter('ndigits', int)
def round_(number, ndigits=0):
    """:yaql:round

    Returns a floating number rounded to ndigits after the decimal point.

    :signature: round(number, ndigits => 0)
    :arg number: input value
    :argType number: number
    :arg ndigits: with how many digits after decimal point to round.
        0 by default
    :argType ndigits: integer
    :returnType: number

    .. code::

        yaql> round(12.52)
        13
        yaql> round(12.52, 1)
        12.5
    """
    return round(number, ndigits)


def is_integer(value):
    """:yaql:isInteger

    Returns true if value is an integer number, otherwise false.

    :signature: isInteger(value)
    :arg value: input value
    :argType value: any
    :returnType: boolean

    .. code::

        yaql> isInteger(12.0)
        false
        yaql> isInteger(12)
        true
    """
    return isinstance(value, int) and not isinstance(value, bool)


def is_number(value):
    """:yaql:isNumber

    Returns true if value is an integer or floating number, otherwise false.

    :signature: isNumber(value)
    :arg value: input value
    :argType value: any
    :returnType: boolean

    .. code::

        yaql> isNumber(12.0)
        true
        yaql> isNumber(12)
        true
    """
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def register(context):
    context.register_function(binary_plus)
    context.register_function(binary_minus)
    context.register_function(multiplication)
    context.register_function(division)
    context.register_function(modulo)
    context.register_function(unary_plus)
    context.register_function(unary_minus)
    context.register_function(abs_)
    context.register_function(gt)
    context.register_function(gte)
    context.register_function(lt)
    context.register_function(lte)
    context.register_function(int_)
    context.register_function(float_)
    context.register_function(random_)
    context.register_function(random__)
    context.register_function(bitwise_and)
    context.register_function(bitwise_or)
    context.register_function(bitwise_not)
    context.register_function(bitwise_xor)
    context.register_function(shift_bits_left)
    context.register_function(shift_bits_right)
    context.register_function(max_)
    context.register_function(min_)
    context.register_function(pow_)
    context.register_function(sign)
    context.register_function(round_)
    context.register_function(is_integer)
    context.register_function(is_number)
