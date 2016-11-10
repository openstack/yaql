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
Functions that produce or consume finite collections - lists, dicts and sets.
"""

import itertools

import six

from yaql.language import specs
from yaql.language import utils
from yaql.language import yaqltypes
import yaql.standard_library.queries


@specs.parameter('args', nullable=True)
@specs.inject('delegate', yaqltypes.Delegate('to_list', method=True))
def list_(delegate, *args):
    """:yaql:list

    Returns list of provided args and unpacks arg element if it's iterable.

    :signature: list([args])
    :arg [args]: arguments to create a list
    :argType [args]: chain of any types
    :returnType: list

    .. code::

        yaql> list(1, "", range(2))
        [1, "", 0, 1]
    """
    def rec(seq):
        for t in seq:
            if utils.is_iterator(t):
                for t2 in rec(t):
                    yield t2
            else:
                yield t
    return delegate(rec(args))


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
def flatten(collection):
    """:yaql:flatten

    Returns an iterator to the recursive traversal of collection.

    :signature: collection.flatten()
    :receiverArg collection: collection to be traversed
    :argType collection: iterable
    :returnType: list

    .. code::

        yaql> ["a", ["b", [2,3]]].flatten()
        ["a", "b", 2, 3]
    """
    for t in collection:
        if utils.is_iterable(t):
            for t2 in flatten(t):
                yield t2
        else:
            yield t


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
def to_list(collection):
    """:yaql:toList

    Returns list built from iterable.

    :signature: collection.toList()
    :receiverArg collection: collection to be transferred to list
    :argType collection: iterable
    :returnType: list

    .. code::

        yaql> range(3).toList()
        [0, 1, 2]
    """
    if isinstance(collection, tuple):
        return collection
    return tuple(collection)


@specs.parameter('args', nullable=True)
@specs.name('#list')
def build_list(engine, *args):
    """:yaql:list

    Returns list of provided args.

    :signature: list([args])
    :arg [args]: arguments to create a list
    :argType [args]: any types
    :returnType: list

    .. code::

        yaql> list(1, "", 2)
        [1, "", 2]
    """
    utils.limit_memory_usage(engine, *((1, t) for t in args))
    return tuple(args)


@specs.no_kwargs
@specs.parameter('args', utils.MappingRule)
def dict_(engine, *args):
    """:yaql:dict

    Returns dictionary of provided keyword values.

    :signature: dict([args])
    :arg [args]: arguments to create a dictionary
    :argType [args]: mappings
    :returnType: dictionary

    .. code::

        yaql> dict(a => 1, b => 2)
        { "a": 1, "b": 2}
    """
    utils.limit_memory_usage(engine, *((1, arg) for arg in args))
    return utils.FrozenDict((t.source, t.destination) for t in args)


@specs.parameter('items', yaqltypes.Iterable())
@specs.no_kwargs
def dict__(items, engine):
    """:yaql:dict

    Returns dictionary with keys and values built on items pairs.

    :signature: dict(items)
    :arg items: list of pairs [key, value] for building dictionary
    :argType items: list
    :returnType: dictionary

    .. code::

        yaql> dict([["a", 2], ["b", 4]])
        {"a": 2, "b": 4}
    """
    result = {}
    for t in items:
        it = iter(t)
        key = next(it)
        value = next(it)
        result[key] = value
        utils.limit_memory_usage(engine, (1, result))
    return utils.FrozenDict(result)


@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('key_selector', yaqltypes.Lambda())
@specs.parameter('value_selector', yaqltypes.Lambda())
@specs.method
def to_dict(collection, engine, key_selector, value_selector=None):
    """:yaql:dict

    Returns dict built on collection where keys are keySelector applied to
    collection elements and values are valueSelector applied to collection
    elements.

    :signature: collection.toDict(keySelector, valueSelector => null)
    :receiverArg collection: collection to build dict from
    :argType collection: iterable
    :arg keySelector: lambda function to get keys from collection elements
    :argType keySelector: lambda
    :arg valueSelector: lambda function to get values from collection elements.
        null by default, which means values to be collection items
    :argType valueSelector: lambda
    :returnType: dictionary

    .. code::

        yaql> [1, 2].toDict($, $ + 1)
        {"1": 2, "2": 3}
    """
    result = {}
    for t in collection:
        key = key_selector(t)
        value = t if value_selector is None else value_selector(t)
        result[key] = value
        utils.limit_memory_usage(engine, (1, result))
    return result


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.parameter('key', yaqltypes.Keyword())
@specs.name('#operator_.')
def dict_keyword_access(d, key):
    """:yaql:operator .

    Returns value of a dictionary by given key.

    :signature: left.right
    :arg left: input dictionary
    :argType left: dictionary
    :arg right: key
    :argType right: keyword
    :returnType: any (appropriate value type)

    .. code::

        yaql> {"a" => 1, "b" => 2}.a
        1
    """
    return d[key]


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('#indexer')
def dict_indexer(d, key):
    """:yaql:operator indexer

    Returns value of a dictionary by given key.

    :signature: left[right]
    :arg left: input dictionary
    :argType left: dictionary
    :arg right: key
    :argType right: keyword
    :returnType: any (appropriate value type)

    .. code::

        yaql> {"a" => 1, "b" => 2}["a"]
        1
    """
    return d[key]


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('#indexer')
def dict_indexer_with_default(d, key, default):
    """:yaql:operator indexer

    Returns value of a dictionary by given key or default if there is
    no such key.

    :signature: left[right, default]
    :arg left: input dictionary
    :argType left: dictionary
    :arg right: key
    :argType right: keyword
    :arg default: default value to be returned if key is missing in dictionary
    :argType default: any
    :returnType: any (appropriate value type)

    .. code::

        yaql> {"a" => 1, "b" => 2}["c", 3]
        3
    """
    return d.get(key, default)


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('get')
@specs.method
def dict_get(d, key, default=None):
    """:yaql:get

    Returns value of a dictionary by given key or default if there is
    no such key.

    :signature: dict.get(key, default => null)
    :receiverArg dict: input dictionary
    :argType dict: dictionary
    :arg key: key
    :argType key: keyword
    :arg default: default value to be returned if key is missing in dictionary.
        null by default
    :argType default: any
    :returnType: any (appropriate value type)

    .. code::

        yaql> {"a" => 1, "b" => 2}.get("c")
        null
        yaql> {"a" => 1, "b" => 2}.get("c", 3)
        3
    """
    return d.get(key, default)


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('set')
@specs.method
@specs.no_kwargs
def dict_set(engine, d, key, value):
    """:yaql:set

    Returns dict with provided key set to value.

    :signature: dict.set(key, value)
    :receiverArg dict: input dictionary
    :argType dict: dictionary
    :arg key: key
    :argType key: keyword
    :arg value: value to be set to input key
    :argType value: any
    :returnType: dictionary

    .. code::

        yaql> {"a" => 1, "b" => 2}.set("c", 3)
        {"a": 1, "b": 2, "c": 3}
        yaql> {"a" => 1, "b" => 2}.set("b", 3)
        {"a": 1, "b": 3}
    """
    utils.limit_memory_usage(engine, (1, d), (1, key), (1, value))
    return utils.FrozenDict(itertools.chain(six.iteritems(d), ((key, value),)))


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.parameter('replacements', utils.MappingType)
@specs.name('set')
@specs.method
@specs.no_kwargs
def dict_set_many(engine, d, replacements):
    """:yaql:set

    Returns dict with replacements keys set to replacements values.

    :signature: dict.set(replacements)
    :receiverArg dict: input dictionary
    :argType dict: dictionary
    :arg replacements: mapping with keys and values to be set on input dict
    :argType key: dictionary
    :returnType: dictionary

    .. code::

        yaql> {"a" => 1, "b" => 2}.set({"b" => 3, "c" => 4})
        {"a": 1, "c": 4, "b": 3}
    """
    utils.limit_memory_usage(engine, (1, d), (1, replacements))
    return utils.FrozenDict(itertools.chain(
        six.iteritems(d), six.iteritems(replacements)))


@specs.no_kwargs
@specs.method
@specs.parameter('args', utils.MappingRule)
@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('set')
def dict_set_many_inline(engine, d, *args):
    """:yaql:set

    Returns dict with args keys set to args values.

    :signature: dict.set([args])
    :receiverArg dict: input dictionary
    :argType dict: dictionary
    :arg [args]: key-values to be set on input dict
    :argType [args]: chain of mappings
    :returnType: dictionary

    .. code::

        yaql> {"a" => 1, "b" => 2}.set("b" => 3, "c" => 4)
        {"a": 1, "c": 4, "b": 3}
    """
    utils.limit_memory_usage(engine, (1, d), *((1, arg) for arg in args))
    return utils.FrozenDict(itertools.chain(
        six.iteritems(d), ((t.source, t.destination) for t in args)))


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('keys')
@specs.method
def dict_keys(d):
    """:yaql:keys

    Returns an iterator over the dictionary keys.

    :signature: dict.keys()
    :receiverArg dict: input dictionary
    :argType dict: dictionary
    :returnType: iterator

    .. code::

        yaql> {"a" => 1, "b" => 2}.keys()
        ["a", "b"]
    """
    return six.iterkeys(d)


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('values')
@specs.method
def dict_values(d):
    """:yaql:values

    Returns an iterator over the dictionary values.

    :signature: dict.values()
    :receiverArg dict: input dictionary
    :argType dict: dictionary
    :returnType: iterator

    .. code::

        yaql> {"a" => 1, "b" => 2}.values()
        [1, 2]
    """
    return six.itervalues(d)


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('items')
@specs.method
def dict_items(d):
    """:yaql:items

    Returns an iterator over pairs [key, value] of input dict.

    :signature: dict.items()
    :receiverArg dict: input dictionary
    :argType dict: dictionary
    :returnType: iterator

    .. code::

        yaql> {"a" => 1, "b" => 2}.items()
        [["a", 1], ["b", 2]]
    """
    return six.iteritems(d)


@specs.parameter('lst', yaqltypes.Sequence(), alias='list')
@specs.parameter('index', int, nullable=False)
@specs.name('#indexer')
def list_indexer(lst, index):
    """:yaql:operator indexer

    Returns value of sequence by given index.

    :signature: left[right]
    :arg left: input sequence
    :argType left: sequence
    :arg right: index
    :argType right: integer
    :returnType: any (appropriate value type)

    .. code::

        yaql> ["a", "b"][0]
        "a"
    """
    return lst[index]


@specs.parameter('value', nullable=True)
@specs.parameter('collection', yaqltypes.Iterable())
@specs.name('#operator_in')
def in_(value, collection):
    """:yaql:operator in

    Returns true if there is at least one occurrence of value in collection,
    false otherwise.

    :signature: left in right
    :arg left: value to be checked for occurrence
    :argType left: any
    :arg right: collection to find occurrence in
    :argType right: iterable
    :returnType: boolean

    .. code::

        yaql> "a" in ["a", "b"]
        true
    """
    return value in collection


@specs.parameter('value', nullable=True)
@specs.parameter('collection', yaqltypes.Iterable())
@specs.method
def contains(collection, value):
    """:yaql:contains

    Returns true if value is contained in collection, false otherwise.

    :signature: collection.contains(value)
    :receiverArg collection: collection to find occurrence in
    :argType collection: iterable
    :arg value: value to be checked for occurrence
    :argType value: any
    :returnType: boolean

    .. code::

        yaql> ["a", "b"].contains("a")
        true
    """
    return value in collection


@specs.parameter('key', nullable=True)
@specs.parameter('d', utils.MappingType, alias='dict')
@specs.method
def contains_key(d, key):
    """:yaql:containsKey

    Returns true if the dictionary contains the key, false otherwise.

    :signature: dict.containsKey(key)
    :receiverArg dict: dictionary to find occurrence in
    :argType dict: mapping
    :arg key: value to be checked for occurrence
    :argType key: any
    :returnType: boolean

    .. code::

        yaql> {"a" => 1, "b" => 2}.containsKey("a")
        true
    """
    return key in d


@specs.parameter('value', nullable=True)
@specs.parameter('d', utils.MappingType, alias='dict')
@specs.method
def contains_value(d, value):
    """:yaql:containsValue

    Returns true if the dictionary contains the value, false otherwise.

    :signature: dict.containsValue(value)
    :receiverArg dict: dictionary to find occurrence in
    :argType dict: mapping
    :arg value: value to be checked for occurrence
    :argType value: any
    :returnType: boolean

    .. code::

        yaql> {"a" => 1, "b" => 2}.containsValue("a")
        false
        yaql> {"a" => 1, "b" => 2}.containsValue(2)
        true
    """
    return value in six.itervalues(d)


@specs.parameter('left', yaqltypes.Iterable())
@specs.parameter('right', yaqltypes.Iterable())
@specs.name('#operator_+')
def combine_lists(left, right, engine):
    """:yaql:operator +

    Returns two iterables concatenated.

    :signature: left + right
    :arg left: left list
    :argType left: iterable
    :arg right: right list
    :argType right: iterable
    :returnType: iterable

    .. code::

        yaql> [1, 2] + [3]
        [1, 2, 3]
    """
    if isinstance(left, tuple) and isinstance(right, tuple):
        utils.limit_memory_usage(engine, (1, left), (1, right))
        return left + right

    elif isinstance(left, frozenset) and isinstance(right, frozenset):
        utils.limit_memory_usage(engine, (1, left), (1, right))
        return left.union(right)

    return yaql.standard_library.queries.concat(left, right)


@specs.parameter('left', yaqltypes.Sequence())
@specs.parameter('right', int)
@specs.name('#operator_*')
def list_by_int(left, right, engine):
    """:yaql:operator *

    Returns sequence repeated count times.

    :signature: left * right
    :arg left: input sequence
    :argType left: sequence
    :arg right: multiplier
    :argType right: integer
    :returnType: sequence

    .. code::

        yaql> [1, 2] * 2
        [1, 2, 1, 2]
    """
    utils.limit_memory_usage(engine, (-right + 1, []), (right, left))
    return left * right


@specs.parameter('left', int)
@specs.parameter('right', yaqltypes.Sequence())
@specs.name('#operator_*')
def int_by_list(left, right, engine):
    """:yaql:operator *

    Returns sequence repeated count times.

    :signature: left * right
    :arg left: multiplier
    :argType left: integer
    :arg right: input sequence
    :argType right: sequence
    :returnType: sequence

    .. code::

        yaql> 2 * [1, 2]
        [1, 2, 1, 2]
    """
    return list_by_int(right, left, engine)


@specs.parameter('left', utils.MappingType)
@specs.parameter('right', utils.MappingType)
@specs.name('#operator_+')
def combine_dicts(left, right, engine):
    """:yaql:operator +

    Returns combined left and right dictionaries.

    :signature: left + right
    :arg left: left dictionary
    :argType left: mapping
    :arg right: right dictionary
    :argType right: mapping
    :returnType: mapping

    .. code::

        yaql> {"a" => 1, b => 2} + {"b" => 3, "c" => 4}
        {"a": 1, "c": 4, "b": 3}
    """
    utils.limit_memory_usage(engine, (1, left), (1, right))
    d = dict(left)
    d.update(right)
    return utils.FrozenDict(d)


def is_list(arg):
    """:yaql:isList

    Returns true if arg is a list, false otherwise.

    :signature: isList(arg)
    :arg arg: value to be checked
    :argType arg: any
    :returnType: boolean

    .. code::

        yaql> isList([1, 2])
        true
        yaql> isList({"a" => 1})
        false
    """
    return utils.is_sequence(arg)


def is_dict(arg):
    """:yaql:isDict

    Returns true if arg is dictionary, false otherwise.

    :signature: isDict(arg)
    :arg arg: value to be checked
    :argType arg: any
    :returnType: boolean

    .. code::

        yaql> isDict([1, 2])
        false
        yaql> isDict({"a" => 1})
        true
    """
    return isinstance(arg, utils.MappingType)


def is_set(arg):
    """:yaql:isSet

    Returns true if arg is set, false otherwise.

    :signature: isSet(arg)
    :arg arg: value to be checked
    :argType arg: any
    :returnType: boolean

    .. code::

        yaql> isSet({"a" => 1})
        false
        yaql> isSet(set(1, 2))
        true
    """
    return isinstance(arg, utils.SetType)


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.extension_method
@specs.name('len')
def dict_len(d):
    """:yaql:len

    Returns size of the dictionary.

    :signature: dict.len()
    :receiverArg dict: input dictionary
    :argType dict: mapping
    :returnType: integer

    .. code::

        yaql> {"a" => 1, "b" => 2}.len()
        2
    """
    return len(d)


@specs.parameter('sequence', yaqltypes.Sequence())
@specs.extension_method
@specs.name('len')
def sequence_len(sequence):
    """:yaql:len

    Returns length of the list.

    :signature: sequence.len()
    :receiverArg sequence: input sequence
    :argType dict: sequence
    :returnType: integer

    .. code::

        yaql> [0, 1, 2].len()
        3
    """
    return len(sequence)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('position', int)
@specs.parameter('count', int)
def delete(collection, position, count=1):
    """:yaql:delete

    Returns collection with removed [position, position+count) elements.

    :signature: collection.delete(position, count => 1)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg position: index to start remove
    :argType position: integer
    :arg count: how many elements to remove, 1 by default
    :argType position: integer
    :returnType: iterable

    .. code::

        yaql> [0, 1, 3, 4, 2].delete(2, 2)
        [0, 1, 2]
    """
    for i, t in enumerate(collection):
        if count >= 0 and not position <= i < position + count:
            yield t
        elif count < 0 and not i >= position:
            yield t


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('position', int)
@specs.parameter('count', int)
def replace(collection, position, value, count=1):
    """:yaql:replace

    Returns collection where [position, position+count) elements are replaced
    with value.

    :signature: collection.replace(position, value, count => 1)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg position: index to start replace
    :argType position: integer
    :arg value: value to be replaced with
    :argType value: any
    :arg count: how many elements to replace, 1 by default
    :argType count: integer
    :returnType: iterable

    .. code::

        yaql> [0, 1, 3, 4, 2].replace(2, 100, 2)
        [0, 1, 100, 2]
    """
    yielded = False
    for i, t in enumerate(collection):
        if (count >= 0 and position <= i < position + count
                or count < 0 and i >= position):
            if not yielded:
                yielded = True
                yield value
        else:
            yield t


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('position', int)
@specs.parameter('count', int)
@specs.parameter('values', yaqltypes.Iterable())
def replace_many(collection, position, values, count=1):
    """:yaql:replaceMany

    Returns collection where [position, position+count) elements are replaced
    with values items.

    :signature: collection.replaceMany(position, values, count => 1)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg position: index to start replace
    :argType position: integer
    :arg values: items to replace
    :argType values: iterable
    :arg count: how many elements to replace, 1 by default
    :argType count: integer
    :returnType: iterable

    .. code::

        yaql> [0, 1, 3, 4, 2].replaceMany(2, [100, 200], 2)
        [0, 1, 100, 200, 2]
    """
    yielded = False
    for i, t in enumerate(collection):
        if (count >= 0 and position <= i < position + count
                or count < 0 and i >= position):
            if not yielded:
                for v in values:
                    yield v
                yielded = True
        else:
            yield t


@specs.method
@specs.name('delete')
@specs.parameter('d', utils.MappingType, alias='dict')
def delete_keys(d, *keys):
    """:yaql:delete

    Returns dict with keys removed.

    :signature: dict.delete([args])
    :receiverArg dict: input dictionary
    :argType dict: mapping
    :arg [args]: keys to be removed from dictionary
    :argType [args]: chain of keywords
    :returnType: mapping

    .. code::

        yaql> {"a" => 1, "b" => 2, "c" => 3}.delete("a", "c")
        {"b": 2}
    """
    return delete_keys_seq(d, keys)


@specs.method
@specs.name('deleteAll')
@specs.parameter('d', utils.MappingType, alias='dict')
@specs.parameter('keys', yaqltypes.Iterable())
def delete_keys_seq(d, keys):
    """:yaql:deleteAll

    Returns dict with keys removed. Keys are provided as an iterable
    collection.

    :signature: dict.deleteAll(keys)
    :receiverArg dict: input dictionary
    :argType dict: mapping
    :arg keys: keys to be removed from dictionary
    :argType keys: iterable
    :returnType: mapping

    .. code::

        yaql> {"a" => 1, "b" => 2, "c" => 3}.deleteAll(["a", "c"])
        {"b": 2}
    """
    copy = dict(d)
    for t in keys:
        copy.pop(t, None)
    return copy


@specs.method
@specs.parameter('collection', yaqltypes.Iterable(validators=[
    lambda x: not isinstance(x, utils.SetType)]
))
@specs.parameter('value', nullable=True)
@specs.parameter('position', int)
@specs.name('insert')
def iter_insert(collection, position, value):
    """:yaql:insert

    Returns collection with inserted value at the given position.

    :signature: collection.insert(position, value)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg position: index for insertion. value is inserted in the end if
        position greater than collection size
    :argType position: integer
    :arg value: value to be inserted
    :argType value: any
    :returnType: iterable

    .. code::

        yaql> [0, 1, 3].insert(2, 2)
        [0, 1, 2, 3]
    """
    i = -1
    for i, t in enumerate(collection):
        if i == position:
            yield value
        yield t

    if position > i:
        yield value


@specs.method
@specs.parameter('collection', yaqltypes.Sequence())
@specs.parameter('value', nullable=True)
@specs.parameter('position', int)
@specs.name('insert')
def list_insert(collection, position, value):
    """:yaql:insert

    Returns collection with inserted value at the given position.

    :signature: collection.insert(position, value)
    :receiverArg collection: input collection
    :argType collection: sequence
    :arg position: index for insertion. value is inserted in the end if
        position greater than collection size
    :argType position: integer
    :arg value: value to be inserted
    :argType value: any
    :returnType: sequence

    .. code::

        yaql> [0, 1, 3].insert(2, 2)
        [0, 1, 2, 3]
    """
    copy = list(collection)
    copy.insert(position, value)
    return copy


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('values', yaqltypes.Iterable())
@specs.parameter('position', int)
def insert_many(collection, position, values):
    """:yaql:insertMany

    Returns collection with inserted values at the given position.

    :signature: collection.insertMany(position, values)
    :receiverArg collection: input collection
    :argType collection: iterable
    :arg position: index for insertion. value is inserted in the end if
        position greater than collection size
    :argType position: integer
    :arg values: items to be inserted
    :argType values: iterable
    :returnType: iterable

    .. code::

        yaql> [0, 1, 3].insertMany(2, [2, 22])
        [0, 1, 2, 22, 3]
    """
    i = -1
    if position < 0:
        for j in values:
            yield j
    for i, t in enumerate(collection):
        if i == position:
            for j in values:
                yield j
        yield t

    if position > i:
        for j in values:
            yield j


@specs.parameter('s', utils.SetType, alias='set')
@specs.extension_method
@specs.name('len')
def set_len(s):
    """:yaql:len

    Returns size of the set.

    :signature: set.len()
    :receiverArg set: input set
    :argType set: set
    :returnType: integer

    .. code::

        yaql> set(0, 1, 2).len()
        3
    """
    return len(s)


@specs.parameter('args', nullable=True)
@specs.inject('delegate', yaqltypes.Delegate('to_set', method=True))
def set_(delegate, *args):
    """:yaql:set

    Returns set initialized with args.

    :signature: set([args])
    :arg [args]: args to build a set
    :argType [args]: chain of any type
    :returnType: set

    .. code::

        yaql> set(0, "", [1, 2])
        [0, "", [1, 2]]
    """
    def rec(seq):
        for t in seq:
            if utils.is_iterator(t):
                for t2 in rec(t):
                    yield t2
            else:
                yield t
    return delegate(rec(args))


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
def to_set(collection):
    """:yaql:toSet

    Returns set built from iterable.

    :signature: collection.toSet()
    :receiverArg collection: collection to build a set
    :argType collection: iterable
    :returnType: set

    .. code::

        yaql> [0, 1, 1, 2].toSet()
        [0, 1, 2]
    """
    return frozenset(collection)


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.method
def union(left, right):
    """:yaql:union

    Returns union of two sets.

    :signature: left.union(right)
    :receiverArg left: input set
    :argType left: set
    :arg right: input set
    :argType right: set
    :returnType: set

    .. code::

        yaql> set(0, 1).union(set(1, 2))
        [0, 1, 2]
    """
    return left.union(right)


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.name('#operator_<')
def set_lt(left, right):
    """:yaql:operator <

    Returns true if left set is subset of right set and left size is strictly
    less than right size, false otherwise.

    :signature: left < right
    :arg left: left set
    :argType left: set
    :arg right: right set
    :argType right: set
    :returnType: boolean

    .. code::

        yaql> set(0) < set(0, 1)
        true
    """
    return left < right


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.name('#operator_<=')
def set_lte(left, right):
    """:yaql:operator <=

    Returns true if left set is subset of right set.

    :signature: left <= right
    :arg left: left set
    :argType left: set
    :arg right: right set
    :argType right: set
    :returnType: boolean

    .. code::

        yaql> set(0, 1) <= set(0, 1)
        true
    """
    return left <= right


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.name('#operator_>=')
def set_gte(left, right):
    """:yaql:operator >=

    Returns true if right set is subset of left set.

    :signature: left >= right
    :arg left: left set
    :argType left: set
    :arg right: right set
    :argType right: set
    :returnType: boolean

    .. code::

        yaql> set(0, 1) >= set(0, 1)
        true
    """
    return left >= right


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.name('#operator_>')
def set_gt(left, right):
    """:yaql:operator >

    Returns true if right set is subset of left set and left size is strictly
    greater than right size, false otherwise.

    :signature: left > right
    :arg left: left set
    :argType left: set
    :arg right: right set
    :argType right: set
    :returnType: boolean

    .. code::

        yaql> set(0, 1) > set(0, 1)
        false
    """
    return left > right


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.method
def intersect(left, right):
    """:yaql:intersect

    Returns set with elements common to left and right sets.

    :signature: left.intersect(right)
    :receiverArg left: left set
    :argType left: set
    :arg right: right set
    :argType right: set
    :returnType: set

    .. code::

        yaql> set(0, 1, 2).intersect(set(0, 1))
        [0, 1]
    """
    return left.intersection(right)


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.method
def difference(left, right):
    """:yaql:difference

    Return the difference of left and right sets as a new set.

    :signature: left.difference(right)
    :receiverArg left: left set
    :argType left: set
    :arg right: right set
    :argType right: set
    :returnType: set

    .. code::

        yaql> set(0, 1, 2).difference(set(0, 1))
        [2]
    """
    return left.difference(right)


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.method
def symmetric_difference(left, right):
    """:yaql:symmetricDifference

    Returns symmetric difference of left and right sets as a new set.

    :signature: left.symmetricDifference(right)
    :receiverArg left: left set
    :argType left: set
    :arg right: right set
    :argType right: set
    :returnType: set

    .. code::

        yaql> set(0, 1, 2).symmetricDifference(set(0, 1, 3))
        [2, 3]
    """
    return left.symmetric_difference(right)


@specs.parameter('s', utils.SetType, alias='set')
@specs.method
@specs.name('add')
def set_add(s, *values):
    """:yaql:add

    Returns a new set with added args.

    :signature: set.add([args])
    :receiverArg set: input set
    :argType set: set
    :arg [args]: values to be added to set
    :argType [args]: chain of any type
    :returnType: set

    .. code::

        yaql> set(0, 1).add("", [1, 2, 3])
        [0, 1, "", [1, 2, 3]]
    """
    return s.union(frozenset(values))


@specs.parameter('s', utils.SetType, alias='set')
@specs.method
@specs.name('remove')
def set_remove(s, *values):
    """:yaql:remove

    Returns the set with excluded values provided in arguments.

    :signature: set.remove([args])
    :receiverArg set: input set
    :argType set: set
    :arg [args]: values to be removed from set
    :argType [args]: chain of any type
    :returnType: set

    .. code::

        yaql> set(0, 1, "", [1, 2, 3]).remove("", 0, [1, 2, 3])
        [1]
    """
    return s.difference(frozenset(values))


def register(context, no_sets=False):
    context.register_function(list_)
    context.register_function(build_list)
    context.register_function(to_list)
    context.register_function(flatten)
    context.register_function(list_indexer)
    context.register_function(dict_)
    context.register_function(dict_, name='#map')
    context.register_function(dict__)
    context.register_function(to_dict)
    context.register_function(dict_keyword_access)
    context.register_function(dict_indexer)
    context.register_function(dict_indexer_with_default)
    context.register_function(dict_get)
    context.register_function(dict_set)
    context.register_function(dict_set_many)
    context.register_function(dict_set_many_inline)
    context.register_function(dict_keys)
    context.register_function(dict_values)
    context.register_function(dict_items)
    context.register_function(in_)
    context.register_function(contains_key)
    context.register_function(contains_value)
    context.register_function(combine_lists)
    context.register_function(list_by_int)
    context.register_function(int_by_list)
    context.register_function(combine_dicts)
    context.register_function(is_dict)
    context.register_function(is_list)
    context.register_function(dict_len)
    context.register_function(sequence_len)
    context.register_function(delete)
    context.register_function(delete_keys)
    context.register_function(delete_keys_seq)
    context.register_function(iter_insert)
    context.register_function(list_insert)
    context.register_function(replace)
    context.register_function(replace_many)
    context.register_function(insert_many)
    context.register_function(contains)

    if not no_sets:
        context.register_function(is_set)
        context.register_function(set_)
        context.register_function(to_set)
        context.register_function(set_len)
        context.register_function(set_lt)
        context.register_function(set_lte)
        context.register_function(set_gt)
        context.register_function(set_gte)
        context.register_function(set_add)
        context.register_function(set_remove)
        context.register_function(union)
        context.register_function(intersect)
        context.register_function(difference)
        context.register_function(
            difference, name='#operator_-', function=True, method=False)
        context.register_function(symmetric_difference)
