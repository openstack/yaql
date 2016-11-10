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
Common module describes comparison operators for different types. Comparing
with null value is considered separately.
"""

from yaql.language import specs


@specs.name('*equal')
def eq(left, right):
    """:yaql:operator =

    Returns true if left and right are equal, false otherwise.

    It is system function and can be used to override behavior
    of comparison between objects.
    """
    return left == right


@specs.name('*not_equal')
def neq(left, right):
    """:yaql:operator !=

    Returns true if left and right are not equal, false otherwise.

    It is system function and can be used to override behavior
    of comparison between objects.
    """
    return left != right


@specs.parameter('right', type(None), nullable=True)
@specs.parameter('left', nullable=False)
@specs.name('#operator_<')
def left_lt_null(left, right):
    """:yaql:operator <

    Returns false. This function is called when left is not null and
    right is null.

    :signature: left < right
    :arg left: left operand
    :argType left: not null
    :arg right: right operand
    :argType right: null
    :returnType: boolean

    .. code:

        yaql> 1 < null
        false
    """
    return False


@specs.parameter('right', type(None), nullable=True)
@specs.parameter('left', nullable=False)
@specs.name('#operator_<=')
def left_lte_null(left, right):
    """:yaql:operator <=

    Returns false. This function is called when left is not null
    and right is null.

    :signature: left <= right
    :arg left: left operand
    :argType left: not null
    :arg right: right operand
    :argType right: null
    :returnType: boolean

    .. code:

        yaql> 1 <= null
        false
    """
    return False


@specs.parameter('right', type(None), nullable=True)
@specs.parameter('left', nullable=False)
@specs.name('#operator_>')
def left_gt_null(left, right):
    """:yaql:operator >

    Returns true. This function is called when left is not null
    and right is null.

    :signature: left > right
    :arg left: left operand
    :argType left: not null
    :arg right: right operand
    :argType right: null
    :returnType: boolean

    .. code:

        yaql> 1 > null
        true
    """
    return True


@specs.parameter('right', type(None), nullable=True)
@specs.parameter('left', nullable=False)
@specs.name('#operator_>=')
def left_gte_null(left, right):
    """:yaql:operator >=

    Returns true. This function is called when left is not null
    and right is null.

    :signature: left >= right
    :arg left: left operand
    :argType left: not null
    :arg right: right operand
    :argType right: null
    :returnType: boolean

    .. code:

        yaql> 1 >= null
        true
    """
    return True


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', nullable=False)
@specs.name('#operator_<')
def null_lt_right(left, right):
    """:yaql:operator <

    Returns true. This function is called when left is null and
    right is not.

    :signature: left < right
    :arg left: left operand
    :argType left: null
    :arg right: right operand
    :argType right: not null
    :returnType: boolean

    .. code:

        yaql> null < 2
        true
    """
    return True


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', nullable=False)
@specs.name('#operator_<=')
def null_lte_right(left, right):
    """:yaql:operator <=

    Returns true. This function is called when left is null and
    right is not.

    :signature: left <= right
    :arg left: left operand
    :argType left: null
    :arg right: right operand
    :argType right: not null
    :returnType: boolean

    .. code:

        yaql> null <= 2
        true
    """
    return True


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', nullable=False)
@specs.name('#operator_>')
def null_gt_right(left, right):
    """:yaql:operator >

    Returns false. This function is called when left is null and right
    is not.

    :signature: left > right
    :arg left: left operand
    :argType left: null
    :arg right: right operand
    :argType right: not null
    :returnType: boolean

    .. code:

        yaql> null > 2
        false
    """
    return False


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', nullable=False)
@specs.name('#operator_>=')
def null_gte_right(left, right):
    """:yaql:operator >=

    Returns false. This function is called when left is null and
    right is not.

    :signature: left >= right
    :arg left: left operand
    :argType left: null
    :arg right: right operand
    :argType right: not null
    :returnType: boolean

    .. code:

        yaql> null >= 2
        false
    """
    return False


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', type(None), nullable=True)
@specs.name('#operator_<')
def null_lt_null(left, right):
    """:yaql:operator <

    Returns false. This function is called when left and right are null.

    :signature: left < right
    :arg left: left operand
    :argType left: null
    :arg right: right operand
    :argType right: null
    :returnType: boolean

    .. code:

        yaql> null < null
        false
    """
    return False


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', type(None), nullable=True)
@specs.name('#operator_<=')
def null_lte_null(left, right):
    """:yaql:operator <=

    Returns true. This function is called when left and right are null.

    :signature: left <= right
    :arg left: left operand
    :argType left: null
    :arg right: right operand
    :argType right: null
    :returnType: boolean

    .. code:

        yaql> null <= null
        true
    """
    return True


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', type(None), nullable=True)
@specs.name('#operator_>')
def null_gt_null(left, right):
    """:yaql:operator >

    Returns false. This function is called when left and right are null.

    :signature: left > right
    :arg left: left operand
    :argType left: null
    :arg right: right operand
    :argType right: null
    :returnType: boolean

    .. code:

        yaql> null > null
        false
    """
    return False


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', type(None), nullable=True)
@specs.name('#operator_>=')
def null_gte_null(left, right):
    """:yaql:operator >=

    Returns true. This function is called when left and right are null.

    :signature: left >= right
    :arg left: left operand
    :argType left: null
    :arg right: right operand
    :argType right: null
    :returnType: boolean

    .. code:

        yaql> null >= null
        true
    """
    return True


def register(context):
    context.register_function(eq)
    context.register_function(neq)
    context.register_function(left_lt_null)
    context.register_function(left_lte_null)
    context.register_function(left_gt_null)
    context.register_function(left_gte_null)

    context.register_function(null_lt_right)
    context.register_function(null_lte_right)
    context.register_function(null_gt_right)
    context.register_function(null_gte_right)

    context.register_function(null_lt_null)
    context.register_function(null_lte_null)
    context.register_function(null_gt_null)
    context.register_function(null_gte_null)
