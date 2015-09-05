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

import itertools

import six

from yaql.language import contexts
from yaql.language import specs
from yaql.language import utils
from yaql.language import yaqltypes


@specs.parameter('name', yaqltypes.StringConstant())
@specs.name('#get_context_data')
def get_context_data(name, context):
    return context[name]


@specs.parameter('expr', yaqltypes.Lambda(method=True))
@specs.name('#operator_.')
def op_dot(receiver, expr):
    return expr(receiver)


@specs.parameter('expr', yaqltypes.YaqlExpression())
@specs.inject('operator', yaqltypes.Delegate('#operator_.'))
@specs.name('#operator_?.')
def elvis_operator(operator, receiver, expr):
    if receiver is None:
        return None
    return operator(receiver, expr)


@specs.parameter('sequence', yaqltypes.Iterable())
@specs.parameter('args', yaqltypes.String())
@specs.method
def unpack(sequence, context, *args):
    lst = tuple(itertools.islice(sequence, len(args) + 1))
    if 0 < len(args) != len(lst):
        raise ValueError('Cannot unpack {0} elements into {1}'.format(
            len(lst), len(args)))
    if len(args) > 0:
        for i in range(len(lst)):
            context[args[i]] = lst[i]
    else:
        for i, t in enumerate(sequence, 1):
            context[str(i)] = t
    return context


def with_(context, *args):
    for i, t in enumerate(args, 1):
        context[str(i)] = t
    return context


@specs.inject('__context__', yaqltypes.Context())
def let(__context__, *args, **kwargs):
    for i, value in enumerate(args, 1):
        __context__[str(i)] = value

    for key, value in six.iteritems(kwargs):
        __context__[key] = value
    return __context__


@specs.parameter('name', yaqltypes.String())
@specs.parameter('func', yaqltypes.Lambda())
def def_(name, func, context):
    @specs.name(name)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    context.register_function(wrapper)
    return context


@specs.parameter('left', contexts.ContextBase)
@specs.parameter('right', yaqltypes.Lambda(with_context=True))
@specs.name('#operator_->')
def send_context(left, right):
    return right(left)


@specs.method
@specs.parameter('condition', yaqltypes.Lambda())
@specs.parameter('message', yaqltypes.String())
def assert__(engine, obj, condition, message=u'Assertion failed'):
    if utils.is_iterator(obj):
        obj = utils.memorize(obj, engine)
    if not condition(obj):
        raise AssertionError(message)
    return obj


@specs.name('#call')
@specs.parameter('callable_', yaqltypes.PythonType(
    object, False, validators=(six.callable,)))
def call(callable_, *args, **kwargs):
    return callable_(*args, **kwargs)


@specs.parameter('func', yaqltypes.Lambda())
def lambda_(func):
    return func


def register(context, delegates=False):
    context.register_function(get_context_data)
    context.register_function(op_dot)
    context.register_function(unpack)
    context.register_function(with_)
    context.register_function(send_context)
    context.register_function(let)
    context.register_function(def_)
    context.register_function(elvis_operator)
    context.register_function(assert__)
    if delegates:
        context.register_function(call)
        context.register_function(lambda_)
