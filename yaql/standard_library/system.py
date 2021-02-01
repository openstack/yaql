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
The module describes main system functions for working with objects.
"""

import itertools

from yaql.language import contexts
from yaql.language import specs
from yaql.language import utils
from yaql.language import yaqltypes


@specs.parameter('name', yaqltypes.StringConstant())
@specs.name('#get_context_data')
def get_context_data(name, context):
    """:yaql:getContextData

    Returns the context value by its name. This function is system
    and can be overridden to change the way of getting context data.

    :signature: getContextData(name)
    :arg name: value's key name
    :argType name: string
    :returnType: any (value type)
    """
    return context[name]


@specs.parameter('expr', yaqltypes.Lambda(method=True))
@specs.name('#operator_.')
def op_dot(receiver, expr):
    """:yaql:operator .

    Returns expr evaluated on receiver.

    :signature: receiver.expr
    :arg receiver: object to evaluate expression
    :argType receiver: any
    :arg expr: expression
    :argType expr: expression that can be evaluated as a method
    :returnType: expression result type

    .. code::

        yaql> [0, 1].select($+1)
        [1, 2]
    """
    return expr(receiver)


@specs.parameter('expr', yaqltypes.YaqlExpression())
@specs.inject('operator', yaqltypes.Delegate('#operator_.'))
@specs.name('#operator_?.')
def elvis_operator(operator, receiver, expr):
    """:yaql:operator ?.

    Evaluates expr on receiver if receiver isn't null and returns the result.
    If receiver is null returns null.

    :signature: receiver?.expr
    :arg receiver: object to evaluate expression
    :argType receiver: any
    :arg expr: expression
    :argType expr: expression that can be evaluated as a method
    :returnType: expression result or null

    .. code::

        yaql> [0, 1]?.select($+1)
        [1, 2]
        yaql> null?.select($+1)
        null
    """
    if receiver is None:
        return None
    return operator(receiver, expr)


@specs.parameter('sequence', yaqltypes.Iterable())
@specs.parameter('args', yaqltypes.String())
@specs.method
def unpack(sequence, context, *args):
    """:yaql:unpack

    Returns context object with sequence values unpacked to args.
    If args size is equal to sequence size then args get appropriate
    sequence values.
    If args size is 0 then args are 1-based indexes.
    Otherwise ValueError is raised.

    :signature: sequence.unpack([args])
    :receiverArg sequence: iterable of items to be passed as context values
    :argType sequence: iterable
    :arg [args]: keys to be associated with sequence items. If args size is
        equal to sequence size then args get appropriate sequence items. If
        args size is 0 then args are indexed start from 1. Otherwise exception
        will be thrown
    :argType [args]: chain of strings
    :returnType: context object

    .. code::

        yaql> [1, 2].unpack(a, b) -> $a + $b
        3
        yaql> [2, 3].unpack() -> $1 + $2
        5
    """
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
    """:yaql:with

    Returns new context object where args are stored with 1-based indexes.

    :signature: with([args])
    :arg [args]: values to be stored under appropriate numbers $1, $2, ...
    :argType [args]: chain of any values
    :returnType: context object

    .. code::

        yaql> with("ab", "cd") -> $1 + $2
        "abcd"
    """
    for i, t in enumerate(args, 1):
        context[str(i)] = t
    return context


@specs.inject('__context__', yaqltypes.Context())
def let(__context__, *args, **kwargs):
    """:yaql:let

    Returns context object where args are stored with 1-based indexes
    and kwargs values are stored with appropriate keys.

    :signature: let([args], {kwargs})
    :arg [args]: values to be stored under appropriate numbers $1, $2, ...
    :argType [args]: chain of any values
    :arg {kwargs}: values to be stored under appropriate keys
    :argType {kwargs}: chain of mappings
    :returnType: context object

    .. code::

        yaql> let(1, 2, a => 3, b => 4) -> $1 + $a + $2 + $b
        10
    """
    for i, value in enumerate(args, 1):
        __context__[str(i)] = value

    for key, value in kwargs.items():
        __context__[key] = value
    return __context__


@specs.parameter('name', yaqltypes.String())
@specs.parameter('func', yaqltypes.Lambda())
def def_(name, func, context):
    """:yaql:def

    Returns new context object with function name defined.

    :signature: def(name, func)
    :arg name: name of function
    :argType name: string
    :arg func: function to be stored under provided name
    :argType func: lambda
    :returnType: context object

    .. code::

        yaql> def(sq, $*$) -> [1, 2, 3].select(sq($))
        [1, 4, 9]
    """
    @specs.name(name)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    context.register_function(wrapper)
    return context


@specs.parameter('left', contexts.ContextBase)
@specs.parameter('right', yaqltypes.Lambda(with_context=True))
@specs.name('#operator_->')
def send_context(left, right):
    """:yaql:operator ->

    Evaluates lambda on provided context and returns the result.

    :signature: left -> right
    :arg left: context to be used for function
    :argType left: context object
    :arg right: function
    :argType right: lambda
    :returnType: any (function return value type)

    .. code::

        yaql> let(a => 1) -> $a
        1
    """
    return right(left)


@specs.method
@specs.parameter('condition', yaqltypes.Lambda())
@specs.parameter('message', yaqltypes.String())
def assert__(engine, obj, condition, message=u'Assertion failed'):
    """:yaql:assert

    Evaluates condition against object. If it evaluates to true returns the
    object, otherwise throws an exception with provided message.

    :signature: obj.assert(condition, message => "Assertion failed")
    :arg obj: object to evaluate condition on
    :argType obj: any
    :arg condition: lambda function to be evaluated on obj. If result of
        function evaluates to false then trows exception message
    :argType condition: lambda
    :arg message: message to trow if condition returns false
    :argType message: string
    :returnType: obj type or message

    .. code::

        yaql> 12.assert($ < 2)
        Execution exception: Assertion failed
        yaql> 12.assert($ < 20)
        12
        yaql> [].assert($, "Failed assertion")
        Execution exception: Failed assertion
    """
    if utils.is_iterator(obj):
        obj = utils.memorize(obj, engine)
    if not condition(obj):
        raise AssertionError(message)
    return obj


@specs.name('#call')
@specs.parameter('callable_', yaqltypes.PythonType(
    object, False, validators=(callable,)))
def call(callable_, *args, **kwargs):
    """:yaql:call

    Evaluates function with specified args and kwargs and returns the
    result.
    This function is used to transform expressions like '$foo(args, kwargs)'
    to '#call($foo, args, kwargs)'.
    Note that to use this functionality 'delegate' mode has to be enabled.

    :signature: call(callable, args, kwargs)
    :arg callable: callable function
    :argType callable: python type
    :arg args: sequence of items to be used for calling
    :argType args: sequence
    :arg kwargs: dictionary with kwargs to be used for calling
    :argType kwargs: mapping
    :returnType: any (callable return type)
    """
    return callable_(*args, **kwargs)


@specs.parameter('func', yaqltypes.Lambda())
def lambda_(func):
    """:yaql:lambda

    Constructs a new anonymous function
    Note that to use this function 'delegate' mode has to be enabled.

    :signature: lambda(func)
    :arg func: function to be returned
    :argType func: lambda
    :returnType: obj type or message

    .. code::

        yaql> let(func => lambda(2 * $)) -> [1, 2, 3].select($func($))
        [2, 4, 6]
        yaql> [1, 2, 3, 4].where(lambda($ > 3)($ + 1))
        [3, 4]
    """
    return func


@specs.name('#operator_.')
@specs.parameter('name', yaqltypes.Keyword())
@specs.inject('func', yaqltypes.Delegate(use_convention=False))
def get_property(func, obj, name):
    """:yaql:operator .

    Returns value of 'name' property.

    :signature: left.right
    :arg left: object
    :argType left: any
    :arg right: object property name
    :argType right: keyword
    :returnType: any

    .. code::

        yaql> now().year
        2016
    """
    func_name = '#property#{0}'.format(name)
    return func(func_name, obj)


@specs.name('call')
@specs.parameter('name', yaqltypes.String())
@specs.parameter('args', yaqltypes.Sequence())
@specs.parameter('kwargs', utils.MappingType)
def call_func(context, engine, name, args, kwargs, receiver=utils.NO_VALUE):
    """:yaql:call

    Evaluates function name with specified args and kwargs and returns the
    result.

    :signature: call(name, args, kwargs)
    :arg name: name of callable
    :argType name: string
    :arg args: sequence of items to be used for calling
    :argType args: sequence
    :arg kwargs: dictionary with kwargs to be used for calling
    :argType kwargs: mapping
    :returnType: any (callable return type)

    .. code::

        yaql> call(let, [1, 2], {a => 3, b => 4}) -> $1 + $a + $2 + $b
        10
    """
    return context(name, engine, receiver)(
        *args, **utils.filter_parameters_dict(kwargs))


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
    context.register_function(call_func)
    if delegates:
        context.register_function(call)
        context.register_function(lambda_)


def register_fallbacks(context):
    context.register_function(get_property)
