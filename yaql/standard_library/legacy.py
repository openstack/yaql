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
The module describes functions which are available with backward compatibility
mode with YAQL v0.2.
Examples are provided with CLI started with legacy mode.
"""

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
    """:yaql:operator =>

    Returns tuple.

    :signature: left => right
    :arg left: left value for tuple
    :argType left: any
    :arg right: right value for tuple
    :argType right: any
    :returnType: tuple

    .. code::

        yaql> a => b
        ["a", "b"]
        yaql> null => 1 => []
        [null, 1, []]
    """
    if isinstance(left, expressions.BinaryOperator) and left.operator == '=>':
        return left(utils.NO_VALUE, context, engine) + (right,)
    else:
        return left(utils.NO_VALUE, context, engine), right


@specs.parameter('tuples', tuple)
@specs.inject('delegate', yaqltypes.Super(with_name=True))
@specs.no_kwargs
@specs.extension_method
def dict_(delegate, *tuples):
    """:yaql:dict

    Returns dict built from tuples.

    :signature: dict([args])
    :arg [args]: chain of tuples to be interpreted as (key, value) for dict
    :argType [args]: chain of tuples
    :returnType: dictionary

    .. code::

        yaql> dict(a => 1, b => 2)
        {"a": 1, "b": 2}
        yaql> dict(tuple(a, 1), tuple(b, 2))
        {"a": 1, "b": 2}
    """
    return delegate('dict', tuples)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
def to_list(collection):
    """:yaql:toList

    Returns collection converted to list.

    :signature: collection.toList()
    :receiverArg collection: collection to be converted
    :argType collection: iterable
    :returnType: list

    .. code::

        yaql> range(0, 3).toList()
        [0, 1, 2]
    """
    return list(collection)


def tuple_(*args):
    """:yaql:tuple

    Returns tuple of args.

    :signature: tuple([args])
    :arg [args]: chain of values for tuple
    :argType [args]: chain of any types
    :returnType: tuple

    .. code::

        yaql> tuple(0, [], "a")
        [0, [], "a"]
    """
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
    """:yaql:range

    Returns sequence from [start, stop).

    :signature: start.range(stop => null)
    :receiverArg start: value to start from
    :argType start: integer
    :arg stop: value to end with. null by default, which means returning
        iterator to sequence
    :argType stop: integer
    :returnType: sequence

    .. code::

        yaql> 0.range(3)
        [0, 1, 2]
        yaql> 0.range().take(4)
        [0, 1, 2, 3]
    """
    if stop is None:
        return itertools.count(start)
    else:
        return six.moves.range(start, stop)


@specs.parameter('conditions', yaqltypes.Lambda(with_context=True))
@specs.no_kwargs
@specs.extension_method
def switch(value, context, *conditions):
    """:yaql:switch

    Returns the value of the first key-value pair for which condition returned
    true. If there is no such returns null.

    :signature: value.switch([args])
    :receiverArg value: value to be used evaluating conditions
    :argType value: any type
    :arg [args]: conditions to be checked for the first true
    :argType [args]: chain of mappings
    :returnType: any (appropriate value type)

    .. code::

        yaql> 15.switch($ < 3 => "a", $ < 7 => "b", $ => "c")
        "c"
    """
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
    """:yaql:as

    Returns context object with mapping functions applied on receiver and
    passed under corresponding keys.

    :signature: receiver.as([args])
    :receiverArg receiver: value to be used for mappings lambdas evaluating
    :argType receiver: any type
    :arg [args]: tuples with lambdas and appropriate keys to be passed to
        context
    :argType [args]: chain of tuples
    :returnType: context object

    .. code::

        yaql> [1, 2].as(len($) => a, sum($) => b) -> $a + $b
        5
    """
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
    """:yaql:operator .

    Returns dict's key value.

    :signature: left.right
    :arg left: input dictionary
    :argType left: mapping
    :arg right: key
    :argType right: keyword
    :returnType: any (appropriate value type)

    .. code::

        yaql> {a => 2, b => 2}.a
        2
    """
    return d.get(key)


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

    for t in ('get', 'list', 'bool', 'int', 'float', 'select', 'where',
              'join', 'sum', 'take_while'):
        for spec in utils.to_extension_method(t, context):
            context.register_function(spec)
