#    Copyright (c) 2013 Mirantis, Inc.
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

import collections
import types
from yaql.exceptions import YaqlExecutionException
from yaql.expressions import Constant, Function
from yaql.functions.decorators import arg, ContextAware, argument, context_aware
from yaql.utils import limit


# basic language operations:
# retrieving data from context, attribution and wrapping in parenthesis

@ContextAware()
def get_context_data(context, path):
    return context.get_data(path())


@arg('self', type=collections.Iterable,
     custom_validator=lambda v: not isinstance(v, types.DictionaryType))
@arg('att_name', constant_only=True)
def collection_attribution(self, att_name):
    def get_att_or_key(item):
        value = att_name
        if hasattr(item, value):
            return getattr(item, value)
        if isinstance(item, types.DictionaryType):
            return item.get(value)
        return None

    for item in self:
        val = get_att_or_key(item)
        if isinstance(val, collections.Iterable) and \
                not isinstance(val, types.StringTypes):
            for v in val:
                yield v
        else:
            yield val


@arg('self', type=types.DictionaryType)
@arg('att_name', constant_only=True)
def dict_attribution(self, att_name):
    return self.get(att_name)


@arg('att_name', constant_only=True)
def obj_attribution(self, att_name):
    return getattr(self(), att_name, None)

@arg('method', eval_arg=False, function_only=True)
def method_call(self, method):
    return method(self)

@context_aware
def testtt(context):
    pass


def wrap(value):
    return value()


# Collection filtering

@arg("index", types.IntType)
def get_by_index(this, index):
    this = this()
    if isinstance(this, types.GeneratorType):
        this = list(this)
    return this[index]


def filter_by_predicate(self, predicate):
    for item in self():
        r = predicate(item)
        if r:
            yield item


# comparison operations

def less_then(a, b):
    return a() < b()


def greater_or_equals(a, b):
    return a() >= b()


def less_or_equals(a, b):
    return a() <= b()


def greater_then(a, b):
    return a() > b()


def equals(a, b):
    return a() == b()


def not_equals(a, b):
    return a() != b()


def is_in(a, b):
    return a() in b()


# arithmetic actions

def plus(a, b):
    return a() + b()


def minus(a, b):
    return a() - b()


def multiply(a, b):
    return a() * b()


def divide(a, b):
    return a() / b()


# Boolean operations

# @EvalArg('a', arg_type=types.BooleanType)
# @EvalArg('b', arg_type=types.BooleanType)
def _and(a, b):
    return a() and b()

# @EvalArg('a', arg_type=types.BooleanType)
# @EvalArg('b', arg_type=types.BooleanType)
def _or(a, b):
    return a() or b()

# @EvalArg('self', arg_type=types.BooleanType)
def _not(self):
    return not self()


#data structure creations

def build_tuple(left, right):
    _list = []
    if left.key == 'operator_=>':
        _list.extend(left())
    else:
        _list.append(left())
    _list.append(right())
    return tuple(_list)


def build_list(*args):
    res = []
    for arg in args:
        arg = arg()
        if isinstance(arg, types.GeneratorType):
            arg = limit(arg)
        res.append(arg)
    return res


def build_dict(*tuples):
    res = {}
    for t in tuples:
        tt = t()
        res[tt[0]] = tt[1]
    return res


# type conversions

def to_int(value):
    return int(value())


def to_float(value):
    return float(value())


@arg('value')
def to_bool(value):
    if isinstance(value, types.StringTypes):
        if value.lower() == 'false':
            return False
    return bool(value)


def add_to_context(context):
    context.register_function(testtt, 'test')


    # basic language operations:
    # retrieving data from context, attribution and wrapping in parenthesis
    context.register_function(get_context_data, 'get_context_data')
    context.register_function(collection_attribution, 'operator_.')
    context.register_function(dict_attribution, 'operator_.')
    context.register_function(obj_attribution, 'operator_.')
    context.register_function(method_call, 'operator_.')
    context.register_function(wrap, 'wrap')



    # collection filtering
    context.register_function(get_by_index, "where")
    context.register_function(filter_by_predicate, "where")

    # comparison operations
    context.register_function(greater_then, 'operator_>')
    context.register_function(less_then, 'operator_<')
    context.register_function(greater_or_equals, 'operator_>=')
    context.register_function(less_or_equals, 'operator_<=')
    context.register_function(equals, 'operator_=')
    context.register_function(not_equals, 'operator_!=')
    context.register_function(is_in, 'operator_in')

    # arithmetic actions
    context.register_function(plus, 'operator_+')
    context.register_function(minus, 'operator_-')
    context.register_function(multiply, 'operator_*')
    context.register_function(divide, 'operator_/')

    # Boolean operations
    context.register_function(_and, 'operator_and')
    context.register_function(_or, 'operator_or')
    context.register_function(_not, 'operator_not')

    #data structure creations
    context.register_function(build_list, 'list')
    context.register_function(build_dict, 'dict')
    context.register_function(build_tuple, 'operator_=>')
    context.register_function(build_tuple, 'operator_=>:')

    #stubs for namespace resolving
    context.register_function(lambda a, b: a() + "." + b(), 'validate')
    context.register_function(lambda a: a(), 'operator_:')

    #type conversions
    context.register_function(to_bool, 'bool')
    context.register_function(to_int, 'int')
    context.register_function(to_float, 'float')
