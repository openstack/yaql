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
import yaql.standard_library.queries


@specs.parameter('args', nullable=True)
@specs.inject('delegate', yaqltypes.Delegate('to_list', method=True))
def list_(delegate, *args):
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
    for t in collection:
        if utils.is_iterable(t):
            for t2 in flatten(t):
                yield t2
        else:
            yield t


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
def to_list(collection):
    if isinstance(collection, tuple):
        return collection
    return tuple(collection)


@specs.parameter('args', nullable=True)
@specs.name('#list')
def build_list(engine, *args):
    utils.limit_memory_usage(engine, *((1, t) for t in args))
    return tuple(args)


@specs.no_kwargs
@specs.parameter('args', utils.MappingRule)
def dict_(engine, *args):
    utils.limit_memory_usage(engine, *((1, arg) for arg in args))
    return utils.FrozenDict((t.source, t.destination) for t in args)


@specs.parameter('items', yaqltypes.Iterable())
@specs.no_kwargs
def dict__(items, engine):
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
    return d[key]


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('#indexer')
def dict_indexer(d, key):
    return d[key]


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('#indexer')
def dict_indexer_with_default(d, key, default):
    return d.get(key, default)


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('get')
@specs.method
def dict_get(d, key, default=None):
    return d.get(key, default)


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('set')
@specs.method
@specs.no_kwargs
def dict_set(engine, d, key, value):
    utils.limit_memory_usage(engine, (1, d), (1, key), (1, value))
    return utils.FrozenDict(itertools.chain(six.iteritems(d), ((key, value),)))


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.parameter('replacements', utils.MappingType)
@specs.name('set')
@specs.method
@specs.no_kwargs
def dict_set_many(engine, d, replacements):
    utils.limit_memory_usage(engine, (1, d), (1, replacements))
    return utils.FrozenDict(itertools.chain(
        six.iteritems(d), six.iteritems(replacements)))


@specs.no_kwargs
@specs.method
@specs.parameter('args', utils.MappingRule)
@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('set')
def dict_set_many_inline(engine, d, *args):
    utils.limit_memory_usage(engine, (1, d), *((1, arg) for arg in args))
    return utils.FrozenDict(itertools.chain(
        six.iteritems(d), ((t.source, t.destination) for t in args)))


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('keys')
@specs.method
def dict_keys(d):
    return six.iterkeys(d)


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('values')
@specs.method
def dict_values(d):
    return six.itervalues(d)


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.name('items')
@specs.method
def dict_items(d):
    return six.iteritems(d)


@specs.parameter('lst', yaqltypes.Sequence(), alias='list')
@specs.parameter('index', int, nullable=False)
@specs.name('#indexer')
def list_indexer(lst, index):
    return lst[index]


@specs.parameter('value', nullable=True)
@specs.parameter('collection', yaqltypes.Iterable())
@specs.name('#operator_in')
def in_(value, collection):
    return value in collection


@specs.parameter('value', nullable=True)
@specs.parameter('collection', yaqltypes.Iterable())
@specs.method
def contains(collection, value):
    return value in collection


@specs.parameter('value', nullable=True)
@specs.parameter('d', utils.MappingType, alias='dict')
@specs.method
def contains_key(d, value):
    return value in d


@specs.parameter('value', nullable=True)
@specs.parameter('d', utils.MappingType, alias='dict')
@specs.method
def contains_value(d, value):
    return value in six.itervalues(d)


@specs.parameter('left', yaqltypes.Iterable())
@specs.parameter('right', yaqltypes.Iterable())
@specs.name('#operator_+')
def combine_lists(left, right, engine):
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
    utils.limit_memory_usage(engine, (-right + 1, []), (right, left))
    return left * right


@specs.parameter('left', int)
@specs.parameter('right', yaqltypes.Sequence())
@specs.name('#operator_*')
def int_by_list(left, right, engine):
    return list_by_int(right, left, engine)


@specs.parameter('left', utils.MappingType)
@specs.parameter('right', utils.MappingType)
@specs.name('#operator_+')
def combine_dicts(left, right, engine):
    utils.limit_memory_usage(engine, (1, left), (1, right))
    d = dict(left)
    d.update(right)
    return utils.FrozenDict(d)


@specs.parameter('left', yaqltypes.Sequence())
@specs.parameter('right', yaqltypes.Sequence())
@specs.name('*equal')
def eq(left, right):
    return left == right


@specs.parameter('left', yaqltypes.Sequence())
@specs.parameter('right', yaqltypes.Sequence())
@specs.name('*not_equal')
def neq(left, right):
    return left != right


@specs.parameter('left', utils.MappingType)
@specs.parameter('right', utils.MappingType)
@specs.name('*equal')
def eq_dict(left, right):
    return left == right


@specs.parameter('left', utils.MappingType)
@specs.parameter('right', utils.MappingType)
@specs.name('*not_equal')
def neq_dict(left, right):
    return left != right


def is_list(arg):
    return utils.is_sequence(arg)


def is_dict(arg):
    return isinstance(arg, utils.MappingType)


def is_set(arg):
    return isinstance(arg, utils.SetType)


@specs.parameter('d', utils.MappingType, alias='dict')
@specs.extension_method
@specs.name('len')
def dict_len(d):
    return len(d)


@specs.parameter('sequence', yaqltypes.Sequence())
@specs.extension_method
@specs.name('len')
def sequence_len(sequence):
    return len(sequence)


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('position', int)
@specs.parameter('count', int)
def delete(collection, position, count=1):
    for i, t in enumerate(collection):
        if count >= 0 and not position <= i < position + count:
            yield t
        elif count < 0 and not i >= position:
            yield t


@specs.method
@specs.parameter('collection', yaqltypes.Iterable([
    lambda t: not is_set(t)
]))
@specs.parameter('position', int)
@specs.parameter('count', int)
def replace(collection, position, value, count=1):
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
    return delete_keys_seq(d, keys)


@specs.method
@specs.name('deleteAll')
@specs.parameter('d', utils.MappingType, alias='dict')
@specs.parameter('keys', yaqltypes.Iterable())
def delete_keys_seq(d, keys):
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
    copy = list(collection)
    copy.insert(position, value)
    return copy


@specs.method
@specs.parameter('collection', yaqltypes.Iterable())
@specs.parameter('values', yaqltypes.Iterable())
@specs.parameter('position', int)
def insert_many(collection, position, values):
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
    return len(s)


@specs.parameter('args', nullable=True)
@specs.inject('delegate', yaqltypes.Delegate('to_set', method=True))
def set_(delegate, *args):
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
    return frozenset(collection)


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.method
def union(left, right):
    return left.union(right)


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.name('*equal')
def set_eq(left, right):
    return left == right


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.name('*not_equal')
def set_neq(left, right):
    return left != right


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.name('#operator_<')
def set_lt(left, right):
    return left < right


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.name('#operator_<=')
def set_lte(left, right):
    return left <= right


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.name('#operator_>=')
def set_gte(left, right):
    return left >= right


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.name('#operator_>')
def set_gt(left, right):
    return left > right


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.method
def intersect(left, right):
    return left.intersection(right)


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.method
def difference(left, right):
    return left.difference(right)


@specs.parameter('left', utils.SetType)
@specs.parameter('right', utils.SetType)
@specs.method
def symmetric_difference(left, right):
    return left.symmetric_difference(right)


@specs.parameter('s', utils.SetType, alias='set')
@specs.method
@specs.name('add')
def set_add(s, *values):
    return s.union(frozenset(values))


@specs.parameter('s', utils.SetType, alias='set')
@specs.method
@specs.name('remove')
def set_remove(s, *values):
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
    context.register_function(eq)
    context.register_function(neq)
    context.register_function(eq_dict)
    context.register_function(neq_dict)
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
        context.register_function(set_eq)
        context.register_function(set_neq)
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
