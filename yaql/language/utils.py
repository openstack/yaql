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

import collections
import re
import sys

from yaql.language import exceptions
from yaql.language import lexer


def create_marker(msg):
    class MarkerClass(object):
        def __repr__(self):
            return msg
    return MarkerClass()


KEYWORD_REGEX = re.compile(lexer.Lexer.t_KEYWORD_STRING.__doc__.strip())
NO_VALUE = create_marker('<NoValue>')


def is_iterator(obj):
    return isinstance(obj, collections.abc.Iterator)


def is_iterable(obj):
    return (
        isinstance(obj, collections.abc.Iterable) and
        not isinstance(obj, (str, MappingType))
    )


def is_sequence(obj):
    return isinstance(obj, collections.abc.Sequence) and not isinstance(
        obj, str)


def is_mutable(obj):
    return isinstance(obj, (collections.abc.MutableSequence,
                            collections.abc.MutableSet,
                            collections.abc.MutableMapping))


SequenceType = collections.abc.Sequence
MutableSequenceType = collections.abc.MutableSequence
SetType = collections.abc.Set
MutableSetType = collections.abc.MutableSet
MappingType = collections.abc.Mapping
MutableMappingType = collections.abc.MutableMapping
IterableType = collections.abc.Iterable
IteratorType = collections.abc.Iterator
QueueType = collections.deque


def convert_input_data(obj, rec=None):
    if rec is None:
        rec = convert_input_data
    if isinstance(obj, str):
        return obj if isinstance(obj, str) else str(obj)
    elif isinstance(obj, SequenceType):
        return tuple(rec(t, rec) for t in obj)
    elif isinstance(obj, MappingType):
        return FrozenDict((rec(key, rec), rec(value, rec))
                          for key, value in obj.items())
    elif isinstance(obj, MutableSetType):
        return frozenset(rec(t, rec) for t in obj)
    elif isinstance(obj, IterableType):
        return map(lambda v: rec(v, rec), obj)
    else:
        return obj


def convert_output_data(obj, limit_func, engine, rec=None):
    if rec is None:
        rec = convert_output_data
    if isinstance(obj, collections.abc.Mapping):
        result = {}
        for key, value in limit_func(obj.items()):
            result[rec(key, limit_func, engine, rec)] = rec(
                value, limit_func, engine, rec)
        return result
    elif isinstance(obj, SetType):
        set_type = list if convert_sets_to_lists(engine) else set
        return set_type(rec(t, limit_func, engine, rec)
                        for t in limit_func(obj))
    elif isinstance(obj, (tuple, list)):
        seq_type = list if convert_tuples_to_lists(engine) else type(obj)
        return seq_type(rec(t, limit_func, engine, rec)
                        for t in limit_func(obj))
    elif is_iterable(obj):
        return list(rec(t, limit_func, engine, rec) for t in limit_func(obj))
    else:
        return obj


def convert_sets_to_lists(engine):
    return engine.options.get('yaql.convertSetsToLists', False)


def convert_tuples_to_lists(engine):
    return engine.options.get('yaql.convertTuplesToLists', True)


class MappingRule(object):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination


class FrozenDict(collections.abc.Mapping):
    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)
        self._hash = None

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def get(self, key, default=None):
        return self._d.get(key, default)

    def __hash__(self):
        if self._hash is None:
            self._hash = 0
            for pair in self.items():
                self._hash ^= hash(pair)
        return self._hash

    def __repr__(self):
        return repr(self._d)


def memorize(collection, engine):
    if not is_iterator(collection):
        return collection

    yielded = []

    class RememberingIterator:
        def __init__(self):
            self.seq = iter(collection)
            self.index = 0

        def __iter__(self):
            return RememberingIterator()

        def __next__(self):
            if self.index < len(yielded):
                self.index += 1
                return yielded[self.index - 1]
            else:
                val = next(self.seq)
                yielded.append(val)
                limit_memory_usage(engine, (1, yielded))
                self.index += 1
                return val

    return RememberingIterator()


def get_max_collection_size(engine):
    return engine.options.get('yaql.limitIterators', -1)


def get_memory_quota(engine):
    return engine.options.get('yaql.memoryQuota', -1)


def limit_iterable(iterable, limit_or_engine):
    if isinstance(limit_or_engine, int):
        max_count = limit_or_engine
    else:
        max_count = get_max_collection_size(limit_or_engine)

    if isinstance(iterable, (SequenceType, MappingType, SetType)):
        if 0 <= max_count < len(iterable):
            raise exceptions.CollectionTooLargeException(max_count)
        return iterable

    def limiting_iterator():
        for i, t in enumerate(iterable):
            if 0 <= max_count <= i:
                raise exceptions.CollectionTooLargeException(max_count)
            yield t
    return limiting_iterator()


def limit_memory_usage(quota_or_engine, *args):
    if isinstance(quota_or_engine, int):
        quota = quota_or_engine
    else:
        quota = get_memory_quota(quota_or_engine)
    if quota <= 0:
        return

    total = 0
    for t in args:
        total += t[0] * sys.getsizeof(t[1], 0)
        if total > quota:
            raise exceptions.MemoryQuotaExceededException()


def to_extension_method(name, context):
    layers = context.collect_functions(
        name,
        lambda t, ctx: not t.is_function or not t.is_method,
        use_convention=True)
    if len(layers) > 1:
        raise ValueError(
            'Multi layer functions are not supported by this helper method')
    if len(layers) > 0:
        for spec in layers[0]:
            spec = spec.clone()
            spec.is_function = True
            spec.is_method = True
            yield spec


def is_keyword(text):
    return KEYWORD_REGEX.match(text) is not None


def filter_parameters_dict(parameters):
    parameters = dict(parameters)
    for name in parameters.keys():
        if not is_keyword(name):
            del parameters[name]
    return parameters
