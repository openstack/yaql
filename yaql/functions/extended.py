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
import random
import types
import itertools
from yaql.context import EvalArg, ContextAware
from yaql.exceptions import YaqlExecutionException
from yaql.utils import limit


def join(self, others, join_predicate, composer):
    for self_item in self():
        for other_item in others():
            if join_predicate(self_item, other_item):
                yield composer(self_item, other_item)


def select(collection, composer):
    for item in collection():
        yield composer(item)


def _sum(this):
    return sum(this())


def _range_limited(start, end):
    for i in xrange(int(start()), int(end())):
        yield i


def _range_infinite(start):
    for i in itertools.count(start()):
        yield i


def rand():
    return random.random()


@EvalArg('self', collections.Iterable)
def take_while(self, predicate):
    for item in self:
        if predicate(item):
            yield item
        else:
            return


@EvalArg('self', types.GeneratorType)
def _list(self):
    return limit(self)


@ContextAware()
@EvalArg('levels', types.IntType)
def parent(context, levels, func):
    con = context
    traversed = 0
    while con:
        if con.data:
            traversed += 1
        if traversed > levels:
            break
        con = con.parent_context
    if con:
        context.data = con.data
    else:
        return None
    return func()


@ContextAware()
def direct_parent(context, func):
    return parent(context, 1, func)

@ContextAware()
def _as(self, context, *tuples):
    self = self()
    for t in tuples:
        tup = t(self)
        val = tup[0]
        key_name = tup[1]
        context.set_data(val, key_name)
    return self

@ContextAware()
def root(context):
    def get_not_null_data(context):
        if context.parent_context:
            data = get_not_null_data(context.parent_context)
            if data:
                return data
        return context.data
    first_data = get_not_null_data(context)
    return first_data.get('$')


def switch(self, *conditions):
    self = self()
    for cond in conditions:
        res = cond(self)
        if not isinstance(res, types.TupleType):
            raise YaqlExecutionException("Switch must have tuple parameters")
        if len(res) != 2:
            raise YaqlExecutionException("Switch tuples must be of size 2")
        if res[0]:
            return res[1]
    return None


def add_to_context(context):
    context.register_function(join, 'join')
    context.register_function(select, 'select')
    context.register_function(_sum, 'sum')
    context.register_function(_range_infinite, 'range')
    context.register_function(_range_limited, 'range')
    context.register_function(rand, 'random')
    context.register_function(_list, 'list')
    context.register_function(take_while, 'takeWhile')
    context.register_function(root, 'root')
    context.register_function(_as, 'as')
    context.register_function(switch, 'switch')
