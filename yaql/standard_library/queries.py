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
def first(collection, default=utils.NO_VALUE):
    try:
        return six.next(iter(collection))
    except StopIteration:
        if default is utils.NO_VALUE:
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
def last(collection, default=utils.NO_VALUE):
    if isinstance(collection, utils.SequenceType):
        if len(collection) == 0:
            if default is utils.NO_VALUE:
                raise StopIteration()
            else:
                return default
        return collection[-1]
    last_value = default
    for t in collection:
        last_value = t
    if last_value is utils.NO_VALUE:
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
def join(engine, collection1, collection2, predicate, selector):
    """:yaql:join

    Returns list of selector applied to those combinations of collection1 and
    collection2 elements, for which predicate is true.

    :signature: collection1.join(collection2, predicate, selector)
    :receiverArg collection1: input collection
    :argType collection1: iterable
    :arg collection2: other input collection
    :argType collection2: iterable
    :arg predicate: function of two arguments to apply to every
        (collection1, collection2) pair, if returned value is true the pair is
        passed to selector
    :argType predicate: lambda
    :arg selector: function of two arguments to apply to every
        (collection1, collection2) pair, for which predicate returned true
    :argType selector: lambda
    :returnType: iterable

    .. code::

        yaql> [1,2,3,4].join([2,5,6], $1 > $2, [$1, $2])
        [[3, 2], [4, 2]]
    """
    collection2 = utils.memorize(collection2, engine)
    for self_item in collection1:
        for other_item in collection2:
            if predicate(self_item, other_item):
                yield selector(self_item, other_item)


@specs.method
@specs.parameter('value', nullable=True)
@specs.parameter('times', int)
def repeat(value, times=-1):
    """:yaql:repeat

    Returns collection with value repeated.

    :signature: value.repeat(times => -1)
    :receiverArg value: value to be repeated
    :argType value: any
    :arg times: how many times repeat value. -1 by default, which means that
        returned value will be an iterator to the endless sequence of values
    :argType times: int
    :returnType: iterable

    .. code::

        yaql> 1.repeat(2)
        [1, 1]
        yaql> 1.repeat().take(3)
        [1, 1, 1]
    """
    if times < 0:
        return itertools.repeat(value)
    else:
        return itertools.repeat(value, times)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
def cycle(collection):
    """:yaql:cycle

    Makes an iterator returning elements from the collection as if it cycled.

    :signature: collection.cycle()
    :receiverArg collection: value to be cycled
    :argType collection: iterable
    :returnType: iterator

    .. code::

        yaql> [1, 2].cycle().take(5)
        [1, 2, 1, 2, 1]
    """
    return itertools.cycle(collection)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
def take_while(collection, predicate):
    """:yaql:takeWhile

    Returns elements from the collection as long as the predicate is true.

    :signature: collection.takeWhile(predicate)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg predicate: function of one argument to apply to every
        collection value
    :argType predicate: lambda
    :returnType: iterable

    .. code::

        yaql> [1, 2, 3, 4, 5].takeWhile($ < 4)
        [1, 2, 3]
    """
    return itertools.takewhile(predicate, collection)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
def skip_while(collection, predicate):
    """:yaql:skipWhile

    Skips elements from the collection as long as the predicate is true.
    Then returns an iterator to collection of remaining elements

    :signature: collection.skipWhile(predicate)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg predicate: function of one argument to apply to every collection value
    :argType predicate: lambda
    :returnType: iterator

    .. code::

        yaql> [1, 2, 3, 4, 5].skipWhile($ < 3)
        [3, 4, 5]
    """
    return itertools.dropwhile(predicate, collection)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
def index_of(collection, item):
    """:yaql:indexOf

    Returns the index in the collection of the first item which value is item.
    -1 is a return value if there is no such item

    :signature: collection.indexOf(item)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg item: value to find in collection
    :argType item: any
    :returnType: integer

    .. code::

        yaql> [1, 2, 3, 2].indexOf(2)
        1
        yaql> [1, 2, 3, 2].indexOf(102)
        -1
    """
    for i, t in enumerate(collection):
        if t == item:
            return i
    return -1


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
def last_index_of(collection, item):
    """:yaql:lastIndexOf

    Returns the index in the collection of the last item which value is item.
    -1 is a return value if there is no such item

    :signature: collection.lastIndexOf(item)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg item: value to find in collection
    :argType item: any
    :returnType: integer

    .. code::

        yaql> [1, 2, 3, 2].lastIndexOf(2)
        3
    """
    index = -1
    for i, t in enumerate(collection):
        if t == item:
            index = i
    return index


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
def index_where(collection, predicate):
    """:yaql:indexWhere

    Returns the index in the collection of the first item which value
    satisfies the predicate. -1 is a return value if there is no such item

    :signature: collection.indexWhere(predicate)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg predicate: function of one argument to apply on every value
    :argType predicate: lambda
    :returnType: integer

    .. code::

        yaql> [1, 2, 3, 2].indexWhere($ > 2)
        2
        yaql> [1, 2, 3, 2].indexWhere($ > 3)
        -1
    """
    for i, t in enumerate(collection):
        if predicate(t):
            return i
    return -1


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
def last_index_where(collection, predicate):
    """:yaql:lastIndexWhere

    Returns the index in the collection of the last item which value
    satisfies the predicate. -1 is a return value if there is no such item

    :signature: collection.lastIndexWhere(predicate)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg predicate: function of one argument to apply on every value
    :argType predicate: lambda
    :returnType: integer

    .. code::

        yaql> [1, 2, 3, 2].lastIndexWhere($ = 2)
        3
    """
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
    """:yaql:slice

    Returns collection divided into list of collections with max size of
    new parts equal to length.

    :signature: collection.slice(length)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg length: max length of new collections
    :argType length: integer
    :returnType: list

    .. code::

        yaql> range(1,6).slice(2)
        [[1, 2], [3, 4], [5]]
    """
    collection = iter(collection)
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
    """:yaql:splitWhere

    Returns collection divided into list of collections where delimiters are
    values for which predicate returns true. Delimiters are deleted from
    result.

    :signature: collection.splitWhere(predicate)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg predicate: function of one argument to be applied on every
        element. Elements for which predicate returns true are delimiters for
        new list
    :argType predicate: lambda
    :returnType: list

    .. code::

        yaql> [1, 2, 3, 4, 5, 6, 7].splitWhere($ mod 3 = 0)
        [[1, 2], [4, 5], [7]]
    """
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
    """:yaql:sliceWhere

    Splits collection into lists. Within every list predicate evaluated
    on its items returns the same value while predicate evaluated on the
    items of the adjacent lists returns different values. Returns an iterator
    to lists.

    :signature: collection.sliceWhere(predicate)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg predicate: function of one argument to be applied on every
        element. Elements for which predicate returns true are delimiters for
        new list and are present in new collection as separate collections
    :argType predicate: lambda
    :returnType: iterator

    .. code::

        yaql> [1, 2, 3, 4, 5, 6, 7].sliceWhere($ mod 3 = 0)
        [[1, 2], [3], [4, 5], [6], [7]]
    """
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
    """:yaql:splitAt

    Splits collection into two lists by index.

    :signature: collection.splitAt(index)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg index: the index of collection to be delimiter for splitting
    :argType index: integer
    :returnType: list

    .. code::

        yaql> [1, 2, 3, 4].splitAt(1)
        [[1], [2, 3, 4]]
        yaql> [1, 2, 3, 4].splitAt(0)
        [[], [1, 2, 3, 4]]
    """
    lst = to_list(collection)
    return [lst[:index], lst[index:]]


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('selector', yaqltypes.Lambda())
def aggregate(collection, selector, seed=utils.NO_VALUE):
    """:yaql:aggregate

    Applies selector of two arguments cumulatively: to the first two elements
    of collection, then to the result of the previous selector applying and
    to the third element, and so on. Returns the result of last selector
    applying.

    :signature: collection.aggregate(selector, seed => NoValue)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg selector: function of two arguments to be applied on every next
        pair of collection
    :argType selector: lambda
    :arg seed: if specified, it is used as start value for accumulating and
        becomes a default when the collection is empty. NoValue by default
    :argType seed: collection elements type
    :returnType: collection elements type

    .. code::

        yaql> [a,a,b,a,a].aggregate($1 + $2)
        "aabaa"
        yaql> [].aggregate($1 + $2, 1)
        1
    """
    if seed is utils.NO_VALUE:
        return six.moves.reduce(selector, collection)
    else:
        return six.moves.reduce(selector, collection, seed)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.inject('to_list', yaqltypes.Delegate('to_list', method=True))
def reverse(collection, to_list):
    """:yaql:reverse

    Returns reversed collection, evaluated to list.

    :signature: collection.reverse()
    :receiverArg collection: input collection
    :argType collection: iterable
    :returnType: list

    .. code::

        yaql> [1, 2, 3, 4].reverse()
        [4, 3, 2, 1]
    """
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
    """:yaql:mergeWith

    Performs a deep merge of two dictionaries.

    :signature: dict.mergeWith(another, listMerger => null,
                               itemMerger => null, maxLevels => null)
    :receiverArg dict: input dictionary
    :argType dict: mapping
    :arg another: dictionary to merge with
    :argType another: mapping
    :arg listMerger: function to be applied while merging two lists. null is a
        default which means listMerger to be distinct(lst1 + lst2)
    :argType listMerger: lambda
    :arg itemMerger: function to be applied while merging two items. null is a
        default, which means itemMerger to be a second item for every pair.
    :argType itemMerger: lambda
    :arg maxLevels: number which describes how deeply merge dicts. 0 by
        default, which means going throughout them
    :argType maxLevels: int
    :returnType: mapping

    .. code::

        yaql> {'a'=> 1, 'b'=> 2, 'c'=> [1, 2]}.mergeWith({'d'=> 5, 'b'=> 3,
                                                          'c'=> [2, 3]})
        {"a": 1, "c": [1, 2, 3], "b": 3, "d": 5}
        yaql> {'a'=> 1, 'b'=> 2, 'c'=> [1, 2]}.mergeWith({'d'=> 5, 'b'=> 3,
                                                          'c'=> [2, 3]},
                                                          $1+$2)
        {"a": 1, "c": [1, 2, 2, 3], "b": 3, "d": 5}
        yaql> {'a'=> 1, 'b'=> 2, 'c'=> [1, 2]}.mergeWith({'d'=> 5, 'b'=> 3,
                                                          'c'=> [2, 3]},
                                                          $1+$2, $1)
        {"a": 1, "c": [1, 2, 2, 3], "b": 2, "d": 5}
        yaql> {'a'=> 1, 'b'=> 2, 'c'=> [1, 2]}.mergeWith({'d'=> 5, 'b'=> 3,
                                                          'c'=> [2, 3]},
                                                          maxLevels => 1)
        {"a": 1, "c": [2, 3], "b": 3, "d": 5}
    """
    if list_merger is None:
        list_merger = lambda lst1, lst2: to_list(
            distinct(engine, lst1 + lst2))
    if item_merger is None:
        item_merger = lambda x, y: y
    return _merge_dicts(d, another, list_merger, item_merger, max_levels)


def is_iterable(value):
    """:yaql:isIterable

    Returns true if value is iterable, false otherwise.

    :signature: isIterable(value)
    :arg value: value to be checked
    :argType value: any
    :returnType: boolean

    .. code::

        yaql> isIterable([])
        true
        yaql> isIterable(set(1,2))
        true
        yaql> isIterable("foo")
        false
        yaql> isIterable({"a" => 1})
        false
    """
    return utils.is_iterable(value)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('selector', yaqltypes.Lambda())
def accumulate(collection, selector, seed=utils.NO_VALUE):
    """:yaql:accumulate

    Applies selector of two arguments cumulatively to the items of collection
    from begin to end, so as to accumulate the collection to a list of
    intermediate values.

    :signature: collection.accumulate(selector, seed => NoValue)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg selector: function of two arguments to be applied on every next
        pair of collection
    :argType selector: lambda
    :arg seed: value to use as the first for accumulating. noValue by default
    :argType seed: collection elements type
    :returnType: list

    .. code::

        yaql> [1, 2, 3].accumulate($1+$2)
        [1, 3, 6]
        yaql> [1, 2, 3].accumulate($1+$2, 100)
        [100, 101, 103, 106]
        yaql> [].accumulate($1+$2,1)
        [1]
    """
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
@specs.parameter('producer', yaqltypes.Lambda())
@specs.parameter('selector', yaqltypes.Lambda())
@specs.parameter('decycle', bool)
def generate(engine, initial, predicate, producer, selector=None,
             decycle=False):
    """:yaql:generate

    Returns iterator to values beginning from initial value with every next
    value produced with producer applied to every previous value, while
    predicate is true.
    Represents traversal over the list where each next element is obtained
    by the lambda result from the previous element.

    :signature: generate(initial, predicate, producer, selector => null,
                         decycle => false)
    :arg initial: value to start from
    :argType initial: any type
    :arg predicate: function of one argument to be applied on every new
        value. Stops generating if return value is false
    :argType predicate: lambda
    :arg producer: function of one argument to produce the next value
    :argType producer: lambda
    :arg selector: function of one argument to store every element in the
        resulted list. none by default which means to store producer result
    :argType selector: lambda
    :arg decycle: return only distinct values if true, false by default
    :argType decycle: boolean
    :returnType: list

    .. code::

        yaql> generate(0, $ < 10, $ + 2)
        [0, 2, 4, 6, 8]
        yaql> generate(1, $ < 10, $ + 2, $ * 1000)
        [1000, 3000, 5000, 7000, 9000]
    """
    past_items = None if not decycle else set()
    while predicate(initial):
        if past_items is not None:
            if initial in past_items:
                break
            past_items.add(initial)
            utils.limit_memory_usage(engine, (1, past_items))
        if selector is None:
            yield initial
        else:
            yield selector(initial)
        initial = producer(initial)


@specs.parameter('producer', yaqltypes.Lambda())
@specs.parameter('selector', yaqltypes.Lambda())
@specs.parameter('decycle', bool)
@specs.parameter('depth_first', bool)
def generate_many(engine, initial, producer, selector=None, decycle=False,
                  depth_first=False):
    """:yaql:generateMany

    Returns iterator to values beginning from initial queue of values with
    every next value produced with producer applied to top of queue, while
    predicate is true.
    Represents tree traversal, where producer is used to get child nodes.

    :signature: generateMany(initial, producer, selector => null,
                             decycle => false, depthFirst => false)
    :arg initial: value to start from
    :argType initial: any type
    :arg producer: function to produce the next value for queue
    :argType producer: lambda
    :arg selector: function of one argument to store every element in the
        resulted list. none by default which means to store producer result
    :argType selector: lambda
    :arg decycle: return only distinct values if true, false by default
    :argType decycle: boolean
    :arg depthFirst: if true puts produced elements to the start of queue,
        false by default
    :argType depthFirst: boolean
    :returnType: list

    .. code::

        yaql> generateMany("1", {"1" => ["2", "3"],
                                 "2"=>["4"], "3"=>["5"]
                                 }.get($, []))
        ["1", "2", "3", "4", "5"]
    """
    past_items = None if not decycle else set()
    queue = utils.QueueType([initial])
    while queue:
        item = queue.popleft()
        if past_items is not None:
            if item in past_items:
                continue
            else:
                past_items.add(item)
                utils.limit_memory_usage(engine, (1, past_items))
        if selector is None:
            yield item
        else:
            yield selector(item)
        produced = producer(item)
        if depth_first:
            len_before = len(queue)
            queue.extend(produced)
            queue.rotate(len(queue) - len_before)
        else:
            queue.extend(produced)
        utils.limit_memory_usage(engine, (1, queue))


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('default', yaqltypes.Iterable())
def default_if_empty(engine, collection, default):
    """:yaql:defaultIfEmpty

    Returns default value if collection is empty.

    :signature: collection.defaultIfEmpty(default)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg default: value to be returned if collection size is 0
    :argType default: iterable
    :returnType: iterable

    .. code::

        yaql> [].defaultIfEmpty([1, 2])
        [1, 2]
    """
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
    context.register_function(generate_many)
    context.register_function(default_if_empty)
