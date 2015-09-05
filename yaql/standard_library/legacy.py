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
from yaql.language import expressions
from yaql.language import specs
from yaql.language import utils
from yaql.language import yaqltypes


@specs.parameter('left', yaqltypes.YaqlExpression())
@specs.name('#operator_=>')
def build_tuple(left, right, context, engine):
    if isinstance(left, expressions.BinaryOperator) and left.operator == '=>':
        return left(utils.NO_VALUE, context, engine) + (right,)
    else:
        return left(utils.NO_VALUE, context, engine), right


@specs.parameter('tuples', tuple)
@specs.inject('delegate', yaqltypes.Super(with_name=True))
@specs.no_kwargs
@specs.extension_method
def dict_(delegate, *tuples):
    return delegate('dict', tuples)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
def to_list(collection):
    return list(collection)


def tuple_(*args):
    return args


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('index_expression', yaqltypes.Lambda())
def indexer(collection, index_expression):
    if isinstance(collection, utils.SequenceType):
        index = index_expression()
        if isinstance(index, int) and not isinstance(index, bool):
            return collection[index]
    return six.moves.filter(index_expression, collection)


@specs.parameter('start', int)
@specs.parameter('stop', int, nullable=True)
@specs.extension_method
def range_(start, stop=None):
    if stop is None:
        return itertools.count(start)
    else:
        return six.moves.range(start, stop)


@specs.parameter('conditions', yaqltypes.Lambda(with_context=True))
@specs.no_kwargs
@specs.extension_method
def switch(value, context, *conditions):
    context = context.create_child_context()
    context[''] = value
    for cond in conditions:
        res = cond(context)
        if isinstance(res, tuple):
            if len(res) != 2:
                raise ValueError('switch() tuples must be of size 2')
            if res[0]:
                return res[1]
        elif isinstance(res, utils.MappingRule):
            if res.source:
                return res.destination
        else:
            raise ValueError('switch() must have tuple or mapping parameters')
    return None


@specs.parameter('receiver', contexts.ContextBase)
@specs.parameter('expr', yaqltypes.Lambda(with_context=True, method=True))
@specs.name('#operator_.')
def op_dot_context(receiver, expr):
    return expr(receiver['$0'], receiver)


@specs.parameter('mappings', yaqltypes.Lambda())
@specs.method
@specs.no_kwargs
def as_(context, receiver, *mappings):
    for t in mappings:
        tt = t(receiver)
        if isinstance(tt, tuple):
            if len(tt) != 2:
                raise ValueError('as() tuples must be of size 2')
            context[tt[1]] = tt[0]
        elif isinstance(tt, utils.MappingRule):
            context[tt.destination] = tt.source
        else:
            raise ValueError('as() must have tuple parameters')
    context['$0'] = receiver
    return context


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.parameter('key', yaqltypes.Keyword())
@specs.name('#operator_.')
def dict_keyword_access(d, key):
    return d.get(key)


@specs.name('*equal')
def eq(left, right):
    return left == right


@specs.name('*not_equal')
def neq(left, right):
    return left != right


def register(context, tuples):
    if tuples:
        context.register_function(build_tuple)
        context.register_function(to_list)
        context.register_function(tuple_)

    context.register_function(dict_)
    context.register_function(dict_, name='#map')
    context.register_function(indexer, name='#indexer', exclusive=True)
    context.register_function(range_)
    context.register_function(switch, exclusive=True)
    context.register_function(as_)
    context.register_function(op_dot_context)
    context.register_function(dict_keyword_access)
    context.register_function(eq)
    context.register_function(neq)

    for t in ('get', 'list', 'bool', 'int', 'float', 'select', 'where',
              'join', 'sum', 'take_while'):
        for spec in utils.to_extension_method(t, context):
            context.register_function(spec)
