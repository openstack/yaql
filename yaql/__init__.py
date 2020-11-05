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

import os.path
import pkg_resources

from yaql.language import contexts
from yaql.language import conventions
from yaql.language import factory
from yaql.language import specs
from yaql.language import utils
from yaql.language import yaqltypes
from yaql.standard_library import boolean as std_boolean
from yaql.standard_library import branching as std_branching
from yaql.standard_library import collections as std_collections
from yaql.standard_library import common as std_common
from yaql.standard_library import date_time as std_datetime
from yaql.standard_library import math as std_math
from yaql.standard_library import queries as std_queries
from yaql.standard_library import regex as std_regex
from yaql.standard_library import strings as std_strings
from yaql.standard_library import system as std_system
from yaql.standard_library import yaqlized as std_yaqlized

_cached_expressions = {}
_cached_engine = None
_default_context = None


def detect_version():
    """
    Detect the installed version of - packages.

    Args:
    """
    try:
        dist = pkg_resources.get_distribution('yaql')
        location = os.path.normcase(dist.location)
        this_location = os.path.normcase(__file__)
        if not this_location.startswith(os.path.join(location, 'yaql')):
            raise pkg_resources.DistributionNotFound()
        return dist.version
    except pkg_resources.DistributionNotFound:
        return 'Undefined (package was not installed with setuptools)'


__version__ = detect_version()


def _setup_context(data, context, finalizer, convention):
    """
    Creates the context.

    Args:
        data: (dict): write your description
        context: (todo): write your description
        finalizer: (bool): write your description
        convention: (todo): write your description
    """
    if context is None:
        context = contexts.Context(
            convention=convention or conventions.CamelCaseConvention())

    if finalizer is None:
        @specs.parameter('iterator', yaqltypes.Iterable())
        @specs.name('#iter')
        def limit(iterator):
            """
            Returns a list of the number of the items.

            Args:
                iterator: (todo): write your description
            """
            return iterator

        @specs.inject('limiter', yaqltypes.Delegate('#iter'))
        @specs.inject('engine', yaqltypes.Engine())
        @specs.name('#finalize')
        def finalize(obj, limiter, engine):
            """
            Finalize the given object.

            Args:
                obj: (todo): write your description
                limiter: (int): write your description
                engine: (todo): write your description
            """
            if engine.options.get('yaql.convertOutputData', True):
                return utils.convert_output_data(obj, limiter, engine)
            return obj

        context.register_function(limit)
        context.register_function(finalize)
    else:
        context.register_function(finalizer)

    if data is not utils.NO_VALUE:
        context['$'] = utils.convert_input_data(data)
    return context


def create_context(data=utils.NO_VALUE, context=None, system=True,
                   common=True, boolean=True, strings=True,
                   math=True, collections=True, queries=True,
                   regex=True, branching=True,
                   no_sets=False, finalizer=None, delegates=False,
                   convention=None, datetime=True, yaqlized=True,
                   group_by_agg_fallback=True):
    """
    Creates a new context.

    Args:
        data: (dict): write your description
        utils: (str): write your description
        NO_VALUE: (str): write your description
        context: (todo): write your description
        system: (todo): write your description
        common: (str): write your description
        boolean: (str): write your description
        strings: (str): write your description
        math: (str): write your description
        collections: (str): write your description
        queries: (list): write your description
        regex: (str): write your description
        branching: (str): write your description
        no_sets: (str): write your description
        finalizer: (bool): write your description
        delegates: (todo): write your description
        convention: (str): write your description
        datetime: (todo): write your description
        yaqlized: (int): write your description
        group_by_agg_fallback: (str): write your description
    """

    context = _setup_context(data, context, finalizer, convention)
    if system:
        std_system.register_fallbacks(context)
        context = context.create_child_context()
        std_system.register(context, delegates)
    if common:
        std_common.register(context)
    if boolean:
        std_boolean.register(context)
    if strings:
        std_strings.register(context)
    if math:
        std_math.register(context)
    if collections:
        std_collections.register(context, no_sets)
    if queries:
        std_queries.register(context, group_by_agg_fallback)
    if regex:
        std_regex.register(context)
    if branching:
        std_branching.register(context)
    if datetime:
        std_datetime.register(context)
    if yaqlized:
        context = std_yaqlized.register(context)

    return context


YaqlFactory = factory.YaqlFactory


def eval(expression, data=None):
    """
    Evaluate an expression.

    Args:
        expression: (bool): write your description
        data: (array): write your description
    """
    global _cached_engine, _cached_expressions, _default_context

    if _cached_engine is None:
        _cached_engine = YaqlFactory().create()

    parsed_expression = _cached_expressions.get(expression)
    if parsed_expression is None:
        parsed_expression = _cached_engine(expression)
        _cached_expressions[expression] = parsed_expression

    if _default_context is None:
        _default_context = create_context()

    return parsed_expression.evaluate(
        data=data, context=_default_context.create_child_context())
