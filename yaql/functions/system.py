#    Copyright (c) 2014 Mirantis, Inc.
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
from yaql.language.exceptions import YaqlExecutionException

from yaql.language.engine import parameter, context_aware, inverse_context


# This unit defines basic YAQL functions, such as
# context retrieval, object property retrieval, method calls etc


def _is_object(value):
    return not isinstance(value, (
        types.DictionaryType, collections.Iterable)) \
        or isinstance(value, types.StringType)


@context_aware
def get_context_data(context, path):
    return context.get_data(path)


@parameter('att_name', constant_only=True)
@parameter('self', custom_validator=_is_object)
def obj_attribution(self, att_name):
    try:
        return getattr(self, att_name)
    except AttributeError:
        raise YaqlExecutionException("Unable to retrieve object attribute")


@parameter('self', arg_type=types.DictionaryType)
@parameter('att_name', constant_only=True)
def dict_attribution(self, att_name):
    return self.get(att_name)


@parameter('method', lazy=True, function_only=True)
@parameter('self')
@inverse_context
def method_call(self, method):
    return method(sender=self)

@context_aware
@parameter('tuple_preds', lazy=True)
def _as(self, context, *tuple_preds):
    self = self
    for t in tuple_preds:
        tup = t(self)
        val = tup[0]
        key_name = tup[1]
        context.set_data(val, key_name)
    return self


@parameter('conditions', lazy=True)
def switch(self, *conditions):
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
    context.register_function(get_context_data)
    context.register_function(obj_attribution, 'operator_.')
    context.register_function(dict_attribution, 'operator_.')
    context.register_function(method_call, 'operator_.')
    context.register_function(_as, 'as')
    context.register_function(switch)

    context.register_function(lambda val: val, 'wrap')
