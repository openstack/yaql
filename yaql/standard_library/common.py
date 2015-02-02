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


@specs.parameter('right', type(None), nullable=True)
@specs.parameter('left', nullable=False)
@specs.name('*equal')
def left_eq_null(left, right):
    return False


@specs.parameter('right', type(None), nullable=True)
@specs.parameter('left', nullable=False)
@specs.name('#operator_<')
def left_lt_null(left, right):
    return False


@specs.parameter('right', type(None), nullable=True)
@specs.parameter('left', nullable=False)
@specs.name('#operator_<=')
def left_lte_null(left, right):
    return False


@specs.parameter('right', type(None), nullable=True)
@specs.parameter('left', nullable=False)
@specs.name('#operator_>')
def left_gt_null(left, right):
    return True


@specs.parameter('right', type(None), nullable=True)
@specs.parameter('left', nullable=False)
@specs.name('#operator_>=')
def left_gte_null(left, right):
    return True


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', nullable=False)
@specs.name('*equal')
def null_eq_right(left, right):
    return False


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', nullable=False)
@specs.name('#operator_<')
def null_lt_right(left, right):
    return True


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', nullable=False)
@specs.name('#operator_<=')
def null_lte_right(left, right):
    return True


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', nullable=False)
@specs.name('#operator_>')
def null_gt_right(left, right):
    return False


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', nullable=False)
@specs.name('#operator_>=')
def null_gte_right(left, right):
    return False


@specs.parameter('right', type(None), nullable=True)
@specs.parameter('left', nullable=False)
@specs.name('*not_equal')
def left_neq_null(left, right):
    return True


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', nullable=False)
@specs.name('*not_equal')
def null_neq_right(left, right):
    return True


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', type(None), nullable=True)
@specs.name('*equal')
def null_eq_null(left, right):
    return True


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', type(None), nullable=True)
@specs.name('*not_equal')
def null_neq_null(left, right):
    return False


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', type(None), nullable=True)
@specs.name('#operator_<')
def null_lt_null(left, right):
    return False


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', type(None), nullable=True)
@specs.name('#operator_<=')
def null_lte_null(left, right):
    return True


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', type(None), nullable=True)
@specs.name('#operator_>')
def null_gt_null(left, right):
    return False


@specs.parameter('left', type(None), nullable=True)
@specs.parameter('right', type(None), nullable=True)
@specs.name('#operator_>=')
def null_gte_null(left, right):
    return True


def register(context):
    context.register_function(left_eq_null)
    context.register_function(left_neq_null)
    context.register_function(left_lt_null)
    context.register_function(left_lte_null)
    context.register_function(left_gt_null)
    context.register_function(left_gte_null)

    context.register_function(null_eq_right)
    context.register_function(null_neq_right)
    context.register_function(null_lt_right)
    context.register_function(null_lte_right)
    context.register_function(null_gt_right)
    context.register_function(null_gte_right)

    context.register_function(null_eq_null)
    context.register_function(null_neq_null)
    context.register_function(null_lt_null)
    context.register_function(null_lte_null)
    context.register_function(null_gt_null)
    context.register_function(null_gte_null)
