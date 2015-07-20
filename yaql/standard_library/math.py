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

import random

import six

from yaql.language import specs
from yaql.language import yaqltypes


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_+')
def binary_plus(left, right):
    return left + right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_-')
def binary_minus(left, right):
    return left - right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_*')
def multiplication(left, right):
    return left * right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_/')
def division(left, right):
    if isinstance(left, six.integer_types) and isinstance(
            right, six.integer_types):
        return left // right
    return left / right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_mod')
def modulo(left, right):
    return left % right


@specs.parameter('op', yaqltypes.Number())
@specs.name('#unary_operator_+')
def unary_plus(op):
    return +op


@specs.parameter('op', yaqltypes.Number())
@specs.name('#unary_operator_-')
def unary_minus(op):
    return -op


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_>')
def gt(left, right):
    return left > right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_>=')
def gte(left, right):
    return left >= right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_<')
def lt(left, right):
    return left < right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('#operator_<=')
def lte(left, right):
    return left <= right


@specs.parameter('op', yaqltypes.Number())
def abs_(op):
    return abs(op)


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('*equal')
def eq(left, right):
    return left == right


@specs.parameter('left', yaqltypes.Number())
@specs.parameter('right', yaqltypes.Number())
@specs.name('*not_equal')
def neq(left, right):
    return left != right


def int_(value):
    if value is None:
        return 0
    return int(value)


def float_(value):
    if value is None:
        return 0.0
    return float(value)


def random_():
    return random.random()


def random__(from_, to_):
    return random.randint(from_, to_)


@specs.parameter('left', int)
@specs.parameter('right', int)
def bitwise_and(left, right):
    return left & right


@specs.parameter('left', int)
@specs.parameter('right', int)
def bitwise_or(left, right):
    return left | right


@specs.parameter('left', int)
@specs.parameter('right', int)
def bitwise_xor(left, right):
    return left ^ right


@specs.parameter('arg', int)
def bitwise_not(arg):
    return ~arg


@specs.parameter('left', int)
@specs.parameter('right', int)
def shift_bits_right(left, right):
    return left >> right


@specs.parameter('left', int)
@specs.parameter('right', int)
def shift_bits_left(left, right):
    return left << right


@specs.parameter('a', nullable=True)
@specs.parameter('b', nullable=True)
@specs.inject('operator', yaqltypes.Delegate('#operator_>'))
def max_(a, b, operator):
    if operator(b, a):
        return b
    return a


@specs.inject('operator', yaqltypes.Delegate('#operator_>'))
def min_(a, b, operator):
    if operator(b, a):
        return a
    return b


@specs.parameter('a', yaqltypes.Number())
@specs.parameter('b', yaqltypes.Number())
@specs.parameter('c', yaqltypes.Number(nullable=True))
def pow_(a, b, c=None):
    return pow(a, b, c)


@specs.parameter('num', yaqltypes.Number())
def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    return 0


@specs.parameter('number', yaqltypes.Number())
@specs.parameter('ndigits', int)
def round_(number, ndigits=0):
    return round(number, ndigits)


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
    context.register_function(eq)
    context.register_function(neq)
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
