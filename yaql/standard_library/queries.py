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

from yaql.language import specs
from yaql.language import utils
from yaql.language import yaqltypes

NO_VALUE = utils.create_marker('NoValue')


class OrderingIterable(utils.IterableType):
    def __init__(self, collection, operator_lt, operator_gt):
        self.collection = collection
        self.operator_lt = operator_lt
        self.operator_gt = operator_gt
        self.order = []
        self.sorted = None

    def append_field(self, selector, is_ascending):
        self.order.append((selector, is_ascending))

    def __iter__(self):
        if self.sorted is None:
            self.do_sort()
        return iter(self.sorted)

    def do_sort(outer_self):
        class Comparator(object):
            @staticmethod
            def compare(left, right):
                result = 0
                for t in outer_self.order:
                    a = t[0](left)
                    b = t[0](right)
                    if outer_self.operator_lt(a, b):
                        result = -1
                    elif outer_self.operator_gt(a, b):
                        result = 1
                    else:
                        continue
                    if not t[1]:
                        result *= -1
                    break
                return result

            def __init__(self, obj):
                self.obj = obj

            def __lt__(self, other):
                return self.compare(self.obj, other.obj) < 0

            def __gt__(self, other):
                return self.compare(self.obj, other.obj) > 0

            def __eq__(self, other):
                return self.compare(self.obj, other.obj) == 0

            def __le__(self, other):
                return self.compare(self.obj, other.obj) <= 0

            def __ge__(self, other):
                return self.compare(self.obj, other.obj) >= 0

            def __ne__(self, other):
                return self.compare(self.obj, other.obj) != 0

        outer_self.sorted = sorted(outer_self.collection, key=Comparator)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
@specs.method
def where(collection, predicate):
    return six.moves.filter(predicate, collection)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('selector', yaqltypes.Lambda())
@specs.method
def select(collection, selector):
    return six.moves.map(selector, collection)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('attribute', yaqltypes.Keyword(expand=False))
@specs.inject('operator', yaqltypes.Delegate('#operator_.'))
@specs.name('#operator_.')
def collection_attribution(collection, attribute, operator):
    return six.moves.map(
        lambda t: operator(t, attribute), collection)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('count', int, nullable=False)
@specs.method
def skip(collection, count):
    return itertools.islice(collection, count, None)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('count', int, nullable=False)
@specs.method
def limit(collection, count):
    return itertools.islice(collection, count)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.extension_method
def append(collection, *args):
    for t in collection:
        yield t
    for t in args:
        yield t


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('key_selector', yaqltypes.Lambda())
@specs.extension_method
def distinct(engine, collection, key_selector=None):
    distinct_values = set()
    for t in collection:
        key = t if key_selector is None else key_selector(t)
        if key not in distinct_values:
            distinct_values.add(key)
            utils.limit_memory_usage(engine, (1, distinct_values))
            yield t


@specs.parameter('collection', yaqltypes.Iterable())
@specs.extension_method
def enumerate_(collection, start=0):
    for i, t in enumerate(collection, start):
        yield [i, t]


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
@specs.extension_method
def any_(collection, predicate=None):
    for t in collection:
        if predicate is None or predicate(t):
            return True
    return False


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
@specs.extension_method
def all_(collection, predicate=None):
    if predicate is None:
        predicate = lambda x: bool(x)

    for t in collection:
        if not predicate(t):
            return False
    return True


@specs.parameter('collections', yaqltypes.Iterable())
@specs.extension_method
def concat(*collections):
    return itertools.chain(*collections)


@specs.parameter('collection', utils.IteratorType)
@specs.name('len')
@specs.extension_method
def count_(collection):
    count = 0
    for t in collection:
        count += 1
    return count


@specs.parameter('collection', yaqltypes.Iterable())
@specs.method
def count(collection):
    return count_(collection)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.method
def memorize(collection, engine):
    return utils.memorize(collection, engine)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.inject('operator', yaqltypes.Delegate('#operator_+'))
@specs.method
def sum_(operator, collection, initial=utils.NO_VALUE):
    return aggregate(collection, operator, initial)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.inject('func', yaqltypes.Delegate('max'))
@specs.method
def max_(func, collection, initial=utils.NO_VALUE):
    return aggregate(collection, func, initial)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.inject('func', yaqltypes.Delegate('min'))
@specs.method
def min_(func, collection, initial=utils.NO_VALUE):
    return aggregate(collection, func, initial)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('default', nullable=True)
@specs.method
def first(collection, default=NO_VALUE):
    try:
        return six.next(iter(collection))
    except StopIteration:
        if default is NO_VALUE:
            raise
        return default


@specs.parameter('collection', yaqltypes.Iterable())
@specs.method
def single(collection):
    it = iter(collection)
    result = six.next(it)
    try:
        six.next(it)
        raise ValueError('Collection contains more than one item')
    except StopIteration:
        return result


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('default', nullable=True)
@specs.method
def last(collection, default=NO_VALUE):
    if isinstance(collection, utils.SequenceType):
        if len(collection) == 0:
            if default is NO_VALUE:
                raise StopIteration()
            else:
                return default
        return collection[-1]
    last_value = default
    for t in collection:
        last_value = t
    if last_value is NO_VALUE:
        raise StopIteration()
    else:
        return last_value


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('selector', yaqltypes.Lambda())
@specs.method
def select_many(collection, selector):
    for item in collection:
        inner = selector(item)
        if utils.is_iterable(inner):
            for t in inner:
                yield t
        else:
            yield inner


@specs.parameter('stop', int)
def range_(stop):
    return iter(six.moves.range(stop))


@specs.parameter('start', int)
@specs.parameter('stop', int)
@specs.parameter('step', int)
def range__(start, stop, step=1):
    return iter(six.moves.range(start, stop, step))


@specs.parameter('start', int)
@specs.parameter('step', int)
def sequence(start=0, step=1):
    return itertools.count(start, step)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('selector', yaqltypes.Lambda())
@specs.inject('operator_gt', yaqltypes.Delegate('#operator_>'))
@specs.inject('operator_lt', yaqltypes.Delegate('#operator_<'))
@specs.method
def order_by(collection, selector, operator_lt, operator_gt):
    oi = OrderingIterable(collection, operator_lt, operator_gt)
    oi.append_field(selector, True)
    return oi


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('selector', yaqltypes.Lambda())
@specs.inject('operator_gt', yaqltypes.Delegate('#operator_>'))
@specs.inject('operator_lt', yaqltypes.Delegate('#operator_<'))
@specs.method
def order_by_descending(collection, selector, operator_lt, operator_gt):
    oi = OrderingIterable(collection, operator_lt, operator_gt)
    oi.append_field(selector, False)
    return oi


@specs.parameter('collection', OrderingIterable)
@specs.parameter('selector', yaqltypes.Lambda())
@specs.method
def then_by(collection, selector, context):
    collection.append_field(selector, True)
    collection.context = context
    return collection


@specs.parameter('collection', OrderingIterable)
@specs.parameter('selector', yaqltypes.Lambda())
@specs.method
def then_by_descending(collection, selector, context):
    collection.append_field(selector, False)
    collection.context = context
    return collection


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('key_selector', yaqltypes.Lambda())
@specs.parameter('value_selector', yaqltypes.Lambda())
@specs.parameter('aggregator', yaqltypes.Lambda())
@specs.method
def group_by(engine, collection, key_selector, value_selector=None,
             aggregator=None):
    groups = {}
    if aggregator is None:
        aggregator = lambda x: x
    for t in collection:
        value = t if value_selector is None else value_selector(t)
        groups.setdefault(key_selector(t), []).append(value)
        utils.limit_memory_usage(engine, (1, groups))
    return select(six.iteritems(groups), aggregator)


@specs.method
@specs.parameter('collections', yaqltypes.Iterable())
def zip_(*collections):
    return six.moves.zip(*collections)


@specs.method
@specs.parameter('collections', yaqltypes.Iterable())
def zip_longest(*collections, **kwargs):
    return six.moves.zip_longest(
        *collections, fillvalue=kwargs.pop('default', None))


@specs.method
@specs.parameter('collection1', yaqltypes.Iterable())
@specs.parameter('collection2', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
@specs.parameter('selector', yaqltypes.Lambda())
def join(collection1, collection2, predicate, selector):
    for self_item in collection1:
        for other_item in collection2:
            if predicate(self_item, other_item):
                yield selector(self_item, other_item)


@specs.method
@specs.parameter('obj', nullable=True)
@specs.parameter('times', int)
def repeat(obj, times=-1):
    if times < 0:
        return itertools.repeat(obj)
    else:
        return itertools.repeat(obj, times)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
def cycle(collection):
    return itertools.cycle(collection)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
def take_while(collection, predicate):
    return itertools.takewhile(predicate, collection)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
def skip_while(collection, predicate):
    return itertools.dropwhile(predicate, collection)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.inject('operator', yaqltypes.Delegate('*equal'))
def index_of(collection, item, operator):
    for i, t in enumerate(collection):
        if operator(t, item):
            return i
    return -1


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.inject('operator', yaqltypes.Delegate('*equal'))
def last_index_of(collection, item, operator):
    index = -1
    for i, t in enumerate(collection):
        if operator(t, item):
            index = i
    return index


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
def index_where(collection, predicate):
    for i, t in enumerate(collection):
        if predicate(t):
            return i
    return -1


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
def last_index_where(collection, predicate):
    index = -1
    for i, t in enumerate(collection):
        if predicate(t):
            index = i
    return index


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('length', int)
@specs.inject('to_list', yaqltypes.Delegate('to_list', method=True))
def slice_(collection, length, to_list):
    while True:
        res = to_list(itertools.islice(collection, length))
        if res:
            yield res
        else:
            break


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
@specs.inject('to_list', yaqltypes.Delegate('to_list', method=True))
def split_where(collection, predicate, to_list):
    lst = to_list(collection)
    start = 0
    end = 0
    while end < len(lst):
        if predicate(lst[end]):
            yield lst[start:end]
            start = end + 1
        end += 1
    if start != end:
        yield lst[start:end]


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
@specs.inject('to_list', yaqltypes.Delegate('to_list', method=True))
def slice_where(collection, predicate, to_list):
    lst = to_list(collection)
    start = 0
    end = 0
    p1 = utils.NO_VALUE
    while end < len(lst):
        p2 = predicate(lst[end])
        if p2 != p1 and p1 is not utils.NO_VALUE:
            yield lst[start:end]
            start = end
        end += 1
        p1 = p2
    if start != end:
        yield lst[start:end]


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('index', int)
@specs.inject('to_list', yaqltypes.Delegate('to_list', method=True))
def split_at(collection, index, to_list):
    lst = to_list(collection)
    return [lst[:index], lst[index:]]


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('selector', yaqltypes.Lambda())
def aggregate(collection, selector, seed=utils.NO_VALUE):
    if seed is utils.NO_VALUE:
        return six.moves.reduce(selector, collection)
    else:
        return six.moves.reduce(selector, collection, seed)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.inject('to_list', yaqltypes.Delegate('to_list', method=True))
def reverse(collection, to_list):
    return reversed(to_list(collection))


def _merge_dicts(dict1, dict2, list_merge_func, item_merger, max_levels=0):
    result = {}
    for key, value1 in six.iteritems(dict1):
        result[key] = value1
        if key in dict2:
            value2 = dict2[key]
            if max_levels != 1 and isinstance(value2, utils.MappingType):
                if not isinstance(value1, utils.MappingType):
                    raise TypeError(
                        'Cannot merge {0} with {1}'.format(
                            type(value1), type(value2)))
                result[key] = _merge_dicts(
                    value1, value2, list_merge_func, item_merger,
                    0 if max_levels == 0 else max_levels - 1)
            elif max_levels != 1 and utils.is_sequence(value2):
                if not utils.is_sequence(value1):
                    raise TypeError(
                        'Cannot merge {0} with {1}'.format(
                            type(value1), type(value2)))
                result[key] = list_merge_func(value1, value2)
            else:
                result[key] = item_merger(value1, value2)

    for key2, value2 in six.iteritems(dict2):
        if key2 not in result:
            result[key2] = value2
    return result


@specs.method
@specs.parameter('d', utils.MappingType, alias='dict')
@specs.parameter('another', utils.MappingType)
@specs.parameter('list_merger', yaqltypes.Lambda())
@specs.parameter('item_merger', yaqltypes.Lambda())
@specs.parameter('max_levels', int)
@specs.inject('to_list', yaqltypes.Delegate('to_list', method=True))
def merge_with(engine, to_list, d, another, list_merger=None,
               item_merger=None, max_levels=0):
    if list_merger is None:
        list_merger = lambda lst1, lst2: to_list(
            distinct(engine, lst1 + lst2))
    if item_merger is None:
        item_merger = lambda x, y: y
    return _merge_dicts(d, another, list_merger, item_merger, max_levels)


def is_iterable(value):
    return utils.is_iterable(value)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('selector', yaqltypes.Lambda())
def accumulate(collection, selector, seed=utils.NO_VALUE):
    it = iter(collection)
    if seed is utils.NO_VALUE:
        try:
            seed = next(it)
        except StopIteration:
            raise TypeError(
                'accumulate() of empty sequence with no initial value')
    yield seed
    total = seed
    for x in it:
        total = selector(total, x)
        yield total


@specs.parameter('predicate', yaqltypes.Lambda())
@specs.parameter('next_', yaqltypes.Lambda())
@specs.parameter('selector', yaqltypes.Lambda())
def generate(initial, predicate, next_, selector=None):
    while predicate(initial):
        if selector is None:
            yield initial
        else:
            yield selector(initial)
        initial = next_(initial)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('default', yaqltypes.Iterable())
def default_if_empty(engine, collection, default):
    if isinstance(collection, (utils.SequenceType, utils.SetType)):
        return default if len(collection) == 0 else collection
    collection = memorize(collection, engine)
    it = iter(collection)
    try:
        next(it)
        return collection
    except StopIteration:
        return default


def register(context):
    context.register_function(where)
    context.register_function(where, name='filter')
    context.register_function(select)
    context.register_function(select, name='map')
    context.register_function(collection_attribution)
    context.register_function(limit)
    context.register_function(limit, name='take')
    context.register_function(skip)
    context.register_function(append)
    context.register_function(distinct)
    context.register_function(enumerate_)
    context.register_function(any_)
    context.register_function(all_)
    context.register_function(concat)
    context.register_function(count_)
    context.register_function(count)
    context.register_function(memorize)
    context.register_function(sum_)
    context.register_function(min_)
    context.register_function(max_)
    context.register_function(first)
    context.register_function(single)
    context.register_function(last)
    context.register_function(select_many)
    context.register_function(range_)
    context.register_function(range__)
    context.register_function(order_by)
    context.register_function(order_by_descending)
    context.register_function(then_by)
    context.register_function(then_by_descending)
    context.register_function(group_by)
    context.register_function(join)
    context.register_function(zip_)
    context.register_function(zip_longest)
    context.register_function(repeat)
    context.register_function(cycle)
    context.register_function(take_while)
    context.register_function(skip_while)
    context.register_function(index_of)
    context.register_function(last_index_of)
    context.register_function(index_where)
    context.register_function(last_index_where)
    context.register_function(slice_)
    context.register_function(split_where)
    context.register_function(slice_where)
    context.register_function(split_at)
    context.register_function(aggregate)
    context.register_function(aggregate, name='reduce')
    context.register_function(accumulate)
    context.register_function(reverse)
    context.register_function(merge_with)
    context.register_function(is_iterable)
    context.register_function(sequence)
    context.register_function(generate)
    context.register_function(default_if_empty)
