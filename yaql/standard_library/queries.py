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
Queries module.
"""

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
    """:yaql:where

    Returns only those collection elements, for which the filtering query
    (predicate) is true.

    :signature: collection.where(predicate)
    :receiverArg collection: collection to be filtered
    :argType collection: iterable
    :arg predicate: filter for collection elements
    :argType predicate: lambda
    :returnType: iterable

    .. code::

        yaql> [1, 2, 3, 4, 5].where($ > 3)
        [4, 5]
    """
    return six.moves.filter(predicate, collection)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('selector', yaqltypes.Lambda())
@specs.method
def select(collection, selector):
    """:yaql:select

    Applies the selector to every item of the collection and returns a list of
    results.

    :signature: collection.select(selector)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg selector: expression for processing elements
    :argType selector: lambda
    :returnType: iterable

    .. code::

        yaql> [1, 2, 3, 4, 5].select($ * $)
        [1, 4, 9, 16, 25]
        yaql> [{'a'=> 2}, {'a'=> 4}].select($.a)
        [2, 4]
    """
    return six.moves.map(selector, collection)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('attribute', yaqltypes.Keyword(expand=False))
@specs.inject('operator', yaqltypes.Delegate('#operator_.'))
@specs.name('#operator_.')
def collection_attribution(collection, attribute, operator):
    """:yaql:operator .

    Retrieves the value of an attribute for each element in a collection and
    returns a list of results.

    :signature: collection.attribute
    :arg collection: input collection
    :argType collection: iterable
    :arg attribute: attribute to get on every collection item
    :argType attribute: keyword
    :returnType: list

    .. code::

        yaql> [{"a" => 1}, {"a" => 2, "b" => 3}].a
        [1, 2]
    """
    return six.moves.map(
        lambda t: operator(t, attribute), collection)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('count', int, nullable=False)
@specs.method
def skip(collection, count):
    """:yaql:skip

    Returns a collection without first count elements.

    :signature: collection.skip(count)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg count: how many elements to skip. If count is greater or equal to
        collection size, return value is empty list
    :argType count: integer
    :returnType: iterable

    .. code::

        yaql> [1, 2, 3, 4, 5].skip(2)
        [3, 4, 5]
    """
    return itertools.islice(collection, count, None)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('count', int, nullable=False)
@specs.method
def limit(collection, count):
    """:yaql:limit

    Returns the first count elements of a collection.

    :signature: collection.limit(count)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg count: how many first elements of a collection to return. If count is
        greater or equal to collection size, return value is input collection
    :argType count: integer
    :returnType: iterable

    .. code::

        yaql> [1, 2, 3, 4, 5].limit(4)
        [1, 2, 3, 4]
    """
    return itertools.islice(collection, count)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.extension_method
def append(collection, *args):
    """:yaql:append

    Returns a collection with appended args.

    :signature: collection.append([args])
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg [args]: arguments to be appended to input collection
    :argType [args]: chain of any types
    :returnType: iterable

    .. code::

        yaql> [1, 2, 3].append(4, 5)
        [1, 2, 3, 4, 5]
    """
    for t in collection:
        yield t
    for t in args:
        yield t


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('key_selector', yaqltypes.Lambda())
@specs.extension_method
def distinct(engine, collection, key_selector=None):
    """:yaql:distinct

    Returns only unique members of the collection. If keySelector is
    specified, it is used to determine uniqueness.

    :signature: collection.distinct(keySelector => null)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg keySelector: specifies a function of one argument that is used
        to extract a comparison key from each collection element. The default
        value is null, which means elements are compared directly
    :argType keySelector: lambda
    :returnType: iterable

    .. code::

        yaql> [1, 2, 3, 1].distinct()
        [1, 2, 3]
        yaql> [{'a'=> 1}, {'b'=> 2}, {'a'=> 1}].distinct()
        [{"a": 1}, {"b": 2}]
        yaql> [['a', 1], ['b', 2], ['c', 1], ['a', 3]].distinct($[1])
        [['a', 1], ['b', 2], ['a', 3]]
    """
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
    """:yaql:enumerate

    Returns an iterator over pairs (index, value), obtained from iterating over
    a collection.

    :signature: collection.enumerate(start => 0)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg start: a value to start with numerating first element of each pair,
        0 is a default value
    :argType start: integer
    :returnType: list

    .. code::

        yaql> ['a', 'b', 'c'].enumerate()
        [[0, 'a'], [1, 'b'], [2, 'c']]
        yaql> ['a', 'b', 'c'].enumerate(2)
        [[2, 'a'], [3, 'b'], [4, 'c']]
    """
    for i, t in enumerate(collection, start):
        yield [i, t]


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
@specs.extension_method
def any_(collection, predicate=None):
    """:yaql:any

    Returns true if a collection is not empty. If a predicate is specified,
    determines whether any element of the collection satisfies the predicate.

    :signature: collection.any(predicate => null)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg predicate: lambda function to apply to every collection value. null
        by default, which means checking collection length
    :argType predicate: lambda
    :returnType: boolean

    .. code::

        yaql> [[], 0, ''].any()
        true
        yaql> [[], 0, ''].any(predicate => $)
        false
    """
    for t in collection:
        if predicate is None or predicate(t):
            return True
    return False


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('predicate', yaqltypes.Lambda())
@specs.extension_method
def all_(collection, predicate=None):
    """:yaql:all

    Returns true if all the elements of a collection evaluate to true.
    If a predicate is specified, returns true if the predicate is true for all
    elements in the collection.

    :signature: collection.all(predicate => null)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg predicate: lambda function to apply to every collection value. null
        by default, which means evaluating collections elements to boolean
        with no predicate
    :argType predicate: lambda
    :returnType: boolean

    .. code::

        yaql> [1, [], ''].all()
        false
        yaql> [1, [0], 'a'].all()
        true
    """
    if predicate is None:
        predicate = lambda x: bool(x)

    for t in collection:
        if not predicate(t):
            return False
    return True


@specs.parameter('collections', yaqltypes.Iterable())
@specs.extension_method
def concat(*collections):
    """:yaql:concat

    Returns an iterator that consequently iterates over elements of the first
    collection, then proceeds to the next collection and so on.

    :signature: collection.concat([args])
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg [args]: iterables to be concatenated with input collection
    :argType [args]: chain of iterable
    :returnType: iterable

    .. code::

        yaql> [1].concat([2, 3], [4, 5])
        [1, 2, 3, 4, 5]
    """
    return itertools.chain(*collections)


@specs.parameter('collection', utils.IteratorType)
@specs.name('len')
@specs.extension_method
def count_(collection):
    """:yaql:len

    Returns the size of the collection.

    :signature: collection.len()
    :receiverArg collection: input collection
    :argType collection: iterable
    :returnType: integer

    .. code::

        yaql> [1, 2].len()
        2
    """
    count = 0
    for t in collection:
        count += 1
    return count


@specs.parameter('collection', yaqltypes.Iterable())
@specs.method
def count(collection):
    """:yaql:count

    Returns the size of the collection.

    :signature: collection.count()
    :receiverArg collection: input collection
    :argType collection: iterable
    :returnType: integer

    .. code::

        yaql> [1, 2].count()
        2
    """
    return count_(collection)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.method
def memorize(collection, engine):
    """:yaql:memorize

    Returns an iterator over collection and memorizes already iterated values.
    This function can be used for iterating over collection several times
    as it remembers elements, and when given collection (iterator) is too
    large to be unwrapped at once.

    :signature: collection.memorize()
    :receiverArg collection: input collection
    :argType collection: iterable
    :returnType: iterator to collection

    .. code::

        yaql> let(range(4)) -> $.sum() + $.len()
        6
        yaql> let(range(4).memorize()) -> $.sum() + $.len()
        10
    """
    return utils.memorize(collection, engine)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.inject('operator', yaqltypes.Delegate('#operator_+'))
@specs.method
def sum_(operator, collection, initial=utils.NO_VALUE):
    """:yaql:sum

    Returns the sum of values in a collection starting from initial if
    specified.

    :signature: collection.sum(initial => NoValue)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg initial: value to start sum with. NoValue by default
    :argType initial: collection's elements type
    :returnType: collection's elements type

    .. code::

        yaql> [3, 1, 2].sum()
        6
        yaql> ['a', 'b'].sum('c')
        "cab"
    """
    return aggregate(collection, operator, initial)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.inject('func', yaqltypes.Delegate('max'))
@specs.method
def max_(func, collection, initial=utils.NO_VALUE):
    """:yaql:max

    Returns max value in collection. Considers initial if specified.

    :signature: collection.max(initial => NoValue)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg initial: value to start with. NoValue by default
    :argType initial: collection's elements type
    :returnType: collection's elements type

    .. code::

        yaql> [3, 1, 2].max()
        3
    """
    return aggregate(collection, func, initial)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.inject('func', yaqltypes.Delegate('min'))
@specs.method
def min_(func, collection, initial=utils.NO_VALUE):
    """:yaql:min

    Returns min value in collection. Considers initial if specified.

    :signature: collection.min(initial => NoValue)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg initial: value to start with. NoValue by default
    :argType initial: collection's elements type
    :returnType: collection's elements type

    .. code::

        yaql> [3, 1, 2].min()
        1
    """
    return aggregate(collection, func, initial)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('default', nullable=True)
@specs.method
def first(collection, default=utils.NO_VALUE):
    """:yaql:first

    Returns the first element of the collection. If the collection is empty,
    returns the default value or raises StopIteration if default is not
    specified.

    :signature: collection.first(default => NoValue)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg default: value to be returned if collection is empty. NoValue by
        default
    :argType default: any
    :returnType: type of collection's elements or default value type

    .. code::

        yaql> [3, 1, 2].first()
        3
    """
    try:
        return six.next(iter(collection))
    except StopIteration:
        if default is utils.NO_VALUE:
            raise
        return default


@specs.parameter('collection', yaqltypes.Iterable())
@specs.method
def single(collection):
    """:yaql:single

    Checks that collection has only one element and returns it. If the
    collection is empty or has more than one element, raises StopIteration.

    :signature: collection.single()
    :receiverArg collection: input collection
    :argType collection: iterable
    :returnType: type of collection's elements

    .. code::

        yaql> ["abc"].single()
        "abc"
        yaql> [1, 2].single()
        Execution exception: Collection contains more than one item
    """
    it = iter(collection)
    result = six.next(it)
    try:
        six.next(it)
    except StopIteration:
        return result
    raise StopIteration('Collection contains more than one item')


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('default', nullable=True)
@specs.method
def last(collection, default=utils.NO_VALUE):
    """:yaql:last

    Returns the last element of the collection. If the collection is empty,
    returns the default value or raises StopIteration if default is not
    specified.

    :signature: collection.last(default => NoValue)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg default: value to be returned if collection is empty. NoValue is
        default value.
    :argType default: any
    :returnType: type of collection's elements or default value type

    .. code::

        yaql> [0, 1, 2].last()
        2
    """
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
    """:yaql:selectMany

    Applies a selector to each element of the collection and returns an
    iterator over results. If the selector returns an iterable object,
    iterates over its elements instead of itself.

    :signature: collection.selectMany(selector)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg selector: function to be applied to every collection element
    :argType selector: lambda
    :returnType: iterator

    .. code::

        yaql> [0, 1, 2].selectMany($ + 2)
        [2, 3, 4]
        yaql> [0, [1, 2], 3].selectMany($ * 2)
        [0, 1, 2, 1, 2, 6]
    """
    for item in collection:
        inner = selector(item)
        if utils.is_iterable(inner):
            for t in inner:
                yield t
        else:
            yield inner


@specs.parameter('stop', int)
def range_(stop):
    """:yaql:range

    Returns an iterator over values from 0 up to stop, not including
    stop, i.e. [0, stop).

    :signature: range(stop)
    :arg stop: right bound for generated list numbers
    :argType stop: integer
    :returnType: iterator

    .. code::

        yaql> range(3)
        [0, 1, 2]
    """
    return iter(six.moves.range(stop))


@specs.parameter('start', int)
@specs.parameter('stop', int)
@specs.parameter('step', int)
def range__(start, stop, step=1):
    """:yaql:range

    Returns an iterator over values from start up to stop, not including stop,
    i.e [start, stop) with step 1 if not specified.

    :signature: range(start, stop, step => 1)
    :arg start: left bound for generated list numbers
    :argType start: integer
    :arg stop: right bound for generated list numbers
    :argType stop: integer
    :arg step: the next element in list is equal to previous + step. 1 is value
        by default
    :argType step: integer
    :returnType: iterator

    .. code::

        yaql> range(1, 4)
        [1, 2, 3]
        yaql> range(4, 1, -1)
        [4, 3, 2]
    """
    return iter(six.moves.range(start, stop, step))


@specs.parameter('start', int)
@specs.parameter('step', int)
def sequence(start=0, step=1):
    """:yaql:sequence

    Returns an iterator to the sequence beginning from start with step.

    :signature: sequence(start => 0, step => 1)
    :arg start: start value of the sequence. 0 is value by default
    :argType start: integer
    :arg step: the next element is equal to previous + step. 1 is value by
        default
    :argType step: integer
    :returnType: iterator

    .. code::

        yaql> sequence().take(5)
        [0, 1, 2, 3, 4]
    """
    return itertools.count(start, step)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('selector', yaqltypes.Lambda())
@specs.inject('operator_gt', yaqltypes.Delegate('#operator_>'))
@specs.inject('operator_lt', yaqltypes.Delegate('#operator_<'))
@specs.method
def order_by(collection, selector, operator_lt, operator_gt):
    """:yaql:orderBy

    Returns an iterator over collection elements sorted in ascending order.
    Selector is applied to each element of the collection to extract
    sorting key.

    :signature: collection.orderBy(selector)
    :receiverArg collection: collection to be ordered
    :argType collection: iterable
    :arg selector: specifies a function of one argument that is used to
        extract a comparison key from each element
    :argType selector: lambda
    :returnType: iterator

    .. code::

        yaql> [[1, 'c'], [2, 'b'], [3, 'c'], [0, 'd']].orderBy($[1])
        [[2, 'b'], [1, 'c'], [3, 'c'], [0, 'd']]
    """
    oi = OrderingIterable(collection, operator_lt, operator_gt)
    oi.append_field(selector, True)
    return oi


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('selector', yaqltypes.Lambda())
@specs.inject('operator_gt', yaqltypes.Delegate('#operator_>'))
@specs.inject('operator_lt', yaqltypes.Delegate('#operator_<'))
@specs.method
def order_by_descending(collection, selector, operator_lt, operator_gt):
    """:yaql:orderByDescending

    Returns an iterator over collection elements sorted in descending order.
    Selector is applied to each element of the collection to extract
    sorting key.

    :signature: collection.orderByDescending(selector)
    :receiverArg collection: collection to be ordered
    :argType collection: iterable
    :arg selector: specifies a function of one argument that is used to
        extract a comparison key from each element
    :argType selector: lambda
    :returnType: iterator

    .. code::

        yaql> [4, 2, 3, 1].orderByDescending($)
        [4, 3, 2, 1]
    """
    oi = OrderingIterable(collection, operator_lt, operator_gt)
    oi.append_field(selector, False)
    return oi


@specs.parameter('collection', OrderingIterable)
@specs.parameter('selector', yaqltypes.Lambda())
@specs.method
def then_by(collection, selector, context):
    """:yaql:thenBy

    To be used with orderBy or orderByDescending. Uses selector to extract
    secondary sort key (ascending) from the elements of the collection and
    adds it to the iterator.

    :signature: collection.thenBy(selector)
    :receiverArg collection: collection to be ordered
    :argType collection: iterable
    :arg selector: specifies a function of one argument that is used to
        extract a comparison key from each element
    :argType selector: lambda
    :returnType: iterator

    .. code::

        yaql> [[3, 'c'], [2, 'b'], [1, 'c']].orderBy($[1]).thenBy($[0])
        [[2, 'b'], [1, 'c'], [3, 'c']]
    """
    collection.append_field(selector, True)
    collection.context = context
    return collection


@specs.parameter('collection', OrderingIterable)
@specs.parameter('selector', yaqltypes.Lambda())
@specs.method
def then_by_descending(collection, selector, context):
    """:yaql:thenByDescending

    To be used with orderBy or orderByDescending. Uses selector to extract
    secondary sort key (descending) from the elements of the collection and
    adds it to the iterator.

    :signature: collection.thenByDescending(selector)
    :receiverArg collection: collection to be ordered
    :argType collection: iterable
    :arg selector: specifies a function of one argument that is used to
        extract a comparison key from each element
    :argType selector: lambda
    :returnType: iterable

    .. code::

        yaql> [[3,'c'], [2,'b'], [1,'c']].orderBy($[1]).thenByDescending($[0])
        [[2, 'b'], [3, 'c'], [1, 'c']]
    """
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
    """:yaql:groupBy

    Returns a collection grouped by keySelector with applied valueSelector as
    values. Returns a list of pairs where the first value is a result value
    of keySelector and the second is a list of values which have common
    keySelector return value.

    :signature: collection.groupBy(keySelector, valueSelector => null,
                                   aggregator => null)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg keySelector: function to be applied to every collection element.
        Values are grouped by return value of this function
    :argType keySelector: lambda
    :arg valueSelector: function to be applied to every collection element to
        put it under appropriate group. null by default, which means return
        element itself
    :argType valueSelector: lambda
    :arg aggregator: function to aggregate value within each group. null by
        default, which means no function to be evaluated on groups
    :argType aggregator: lambda
    :returnType: list

    .. code::

        yaql> [["a", 1], ["b", 2], ["c", 1], ["d", 2]].groupBy($[1], $[0])
        [[1, ["a", "c"]], [2, ["b", "d"]]]
        yaql> [["a", 1], ["b", 2], ["c", 1]].groupBy($[1], $[0], $.sum())
        [[1, "ac"], [2, "b"]]
    """
    groups = {}
    if aggregator is None:
        new_aggregator = lambda x: x
    else:
        new_aggregator = lambda x: (x[0], aggregator(x[1]))
    for t in collection:
        value = t if value_selector is None else value_selector(t)
        groups.setdefault(key_selector(t), []).append(value)
        utils.limit_memory_usage(engine, (1, groups))
    return select(six.iteritems(groups), new_aggregator)


@specs.method
@specs.parameter('collections', yaqltypes.Iterable())
def zip_(*collections):
    """:yaql:zip

    Returns an iterator over collections, where the n-th iterable contains the
    n-th element from each of collections. Stops iterating as soon as any of
    the collections is exhausted.

    :signature: collection.zip([args])
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg [args]: collections for zipping with input collection
    :argType [args]: chain of collections
    :returnType: iterator

    .. code::

        yaql> [1, 2, 3].zip([4, 5], [6, 7])
        [[1, 4, 6], [2, 5, 7]]
    """
    return six.moves.zip(*collections)


@specs.method
@specs.parameter('collections', yaqltypes.Iterable())
def zip_longest(*collections, **kwargs):
    """:yaql:zipLongest

    Returns an iterator over collections, where the n-th iterable contains
    the n-th element from each of collections. Iterates until all the
    collections are not exhausted and fills lacking values with default value,
    which is null by default.

    :signature: collection.zipLongest([args], default => null)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg [args]: collections for zipping with input collection
    :argType [args]: chain of collections
    :arg default: default value for lacking values, can be passed only
        as keyword argument. null by default
    :argType default: any type
    :returnType: iterator

    .. code::

        yaql> [1, 2, 3].zipLongest([4, 5])
        [[1, 4], [2, 5], [3, null]]
        yaql> [1, 2, 3].zipLongest([4, 5], default => 100)
        [[1, 4], [2, 5], [3, 100]]
    """
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
