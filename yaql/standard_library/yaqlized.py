#    Copyright (c) 2016 Mirantis, Inc.
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
Any Python class or object can be yaqlized. It is possible to call methods,
access attributes/properties and index of yaqlized objects.

The first way to yaqlize object is using function call:

.. code-block:: python

    class A(object):
        foo = 256
        def bar(self):
            print('yaqlization works with methods too')

    sample_object = A()
    yaqlization.yaqlize(sample_object)

The second way is using decorator:

.. code-block:: python

    @yaqlization.yaqlize
    class A(object):
        foo = 256
        def bar(self):
            print('yaqlization works with methods too')

Any mentioned operation on yaqlized objects can be disabled with additional
parameters for yaqlization. Also it is possible to specify whitelist/blacklist
of methods/attributes/keys that are exposed to the yaql.

This module provides implemented operators on Yaqlized objects.
"""


import re

import six

from yaql.language import expressions
from yaql.language import runner
from yaql.language import specs
from yaql.language import utils
from yaql.language import yaqltypes
from yaql import yaqlization


REGEX_TYPE = type(re.compile('.'))


class Yaqlized(yaqltypes.GenericType):
    def __init__(self, can_access_attributes=False, can_call_methods=False,
                 can_index=False):
        def check_value(value, context, *args, **kwargs):
            settings = yaqlization.get_yaqlization_settings(value)
            if settings is None:
                return False
            if can_access_attributes and not settings['yaqlizeAttributes']:
                return False
            if can_call_methods and not settings['yaqlizeMethods']:
                return False
            if can_index and not settings['yaqlizeIndexer']:
                return False
            return True

        super(Yaqlized, self).__init__(checker=check_value, nullable=False)


def _match_name_to_entry(name, entry):
    if name == entry:
        return True
    elif isinstance(entry, REGEX_TYPE):
        return entry.search(name) is not None
    elif six.callable(entry):
        return entry(name)
    return False


def _validate_name(name, settings, exception_cls=AttributeError):
    if name.startswith('_'):
        raise exception_cls('Cannot access ' + name)
    whitelist = settings['whitelist']
    if whitelist:
        for entry in whitelist:
            if _match_name_to_entry(name, entry):
                return
        raise exception_cls('Cannot access ' + name)
    blacklist = settings['blacklist']
    if blacklist:
        for entry in blacklist:
            if _match_name_to_entry(name, entry):
                raise exception_cls('Cannot access ' + name)


def _remap_name(name, settings):
    return settings['attributeRemapping'].get(name, name)


def _auto_yaqlize(value, settings):
    if not settings['autoYaqlizeResult']:
        return
    if isinstance(value, type):
        cls = value
    else:
        cls = type(value)
    if cls.__module__ == int.__module__:
        return
    try:
        yaqlization.yaqlize(value, auto_yaqlize_result=True)
    except Exception:
        pass


@specs.parameter('receiver', Yaqlized(can_call_methods=True))
@specs.parameter('expr', yaqltypes.YaqlExpression(expressions.Function))
@specs.name('#operator_.')
def op_dot(receiver, expr, context, engine):
    """:yaql:operator .

    Evaluates expression on receiver and returns its result.

    :signature: receiver.expr
    :arg receiver: yaqlized receiver
    :argType receiver: yaqlized object, initialized with
        yaqlize_methods equal to True
    :arg expr: expression to be evaluated
    :argType expr: expression
    :returnType: any (expression return type)
    """
    settings = yaqlization.get_yaqlization_settings(receiver)
    mappings = _remap_name(expr.name, settings)

    _validate_name(expr.name, settings)
    if not isinstance(mappings, six.string_types):
        name = mappings[0]
        if len(mappings) > 0:
            arg_mappings = mappings[1]
        else:
            arg_mappings = {}
    else:
        name = mappings
        arg_mappings = {}

    func = getattr(receiver, name)
    args, kwargs = runner.translate_args(False, expr.args, {})
    args = tuple(arg(utils.NO_VALUE, context, engine) for arg in args)
    for key, value in six.iteritems(kwargs):
        kwargs[arg_mappings.get(key, key)] = value(
            utils.NO_VALUE, context, engine)
    res = func(*args, **kwargs)
    _auto_yaqlize(res, settings)
    return res


@specs.parameter('obj', Yaqlized(can_access_attributes=True))
@specs.parameter('attr', yaqltypes.Keyword())
@specs.name('#operator_.')
def attribution(obj, attr):
    """:yaql:operator .

    Returns attribute of the object.

    :signature: obj.attr
    :arg obj: yaqlized object
    :argType obj: yaqlized object, initialized with
        yaqlize_attributes equal to True
    :arg attr: attribute name
    :argType attr: keyword
    :returnType: any
    """
    settings = yaqlization.get_yaqlization_settings(obj)
    _validate_name(attr, settings)
    attr = _remap_name(attr, settings)
    res = getattr(obj, attr)
    _auto_yaqlize(res, settings)
    return res


@specs.parameter('obj', Yaqlized(can_index=True))
@specs.name('#indexer')
def indexation(obj, key):
    """:yaql:operator indexer

    Returns value of attribute/property key of the object.

    :signature: obj[key]
    :arg obj: yaqlized object
    :argType obj: yaqlized object, initialized with
        yaqlize_indexer equal to True
    :arg key: index name
    :argType key: keyword
    :returnType: any
    """
    settings = yaqlization.get_yaqlization_settings(obj)
    _validate_name(key, settings, KeyError)
    res = obj[key]
    _auto_yaqlize(res, settings)
    return res


def register(context):
    context = context.create_child_context()
    context.register_function(op_dot)
    context.register_function(attribution)
    context.register_function(indexation)
    return context
