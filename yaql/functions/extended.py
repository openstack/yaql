import collections
import random
import types
import itertools
from yaql.context import EvalArg


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
    return list(self)


def add_to_context(context):
    context.register_function(join, 'join')
    context.register_function(select, 'select')
    context.register_function(_sum, 'sum')
    context.register_function(_range_infinite, 'range')
    context.register_function(_range_limited, 'range')
    context.register_function(rand, 'random')
    context.register_function(_list, 'list')
    context.register_function(take_while, 'takeWhile')
