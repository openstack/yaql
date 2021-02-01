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

# flake8: noqa: E731

import sys

from yaql.language import exceptions
from yaql.language import expressions
from yaql.language import utils
from yaql.language import yaqltypes


def call(name, context, args, kwargs, engine, receiver=utils.NO_VALUE,
         data_context=None, use_convention=False, function_filter=None):

    if data_context is None:
        data_context = context

    if function_filter is None:
        function_filter = lambda fd, ctx: True

    if receiver is utils.NO_VALUE:
        predicate = lambda fd, ctx: fd.is_function and function_filter(fd, ctx)
    else:
        predicate = lambda fd, ctx: fd.is_method and function_filter(fd, ctx)

    all_overloads = context.collect_functions(
        name, predicate, use_convention=use_convention)

    if not all_overloads:
        if receiver is utils.NO_VALUE:
            raise exceptions.NoFunctionRegisteredException(name)
        else:
            raise exceptions.NoMethodRegisteredException(name, receiver)
    else:
        delegate = choose_overload(
            name, all_overloads, engine, receiver, data_context, args, kwargs)
        try:
            result = delegate()
            utils.limit_memory_usage(engine, (1, result))
            return result
        except StopIteration as e:
            raise exceptions.WrappedException(e).with_traceback(
                sys.exc_info()[2])


def choose_overload(name, candidates, engine, receiver, context, args, kwargs):
    def raise_ambiguous():
        if receiver is utils.NO_VALUE:
            raise exceptions.AmbiguousFunctionException(name)
        else:
            raise exceptions.AmbiguousMethodException(name, receiver)

    def raise_not_found():
        if receiver is utils.NO_VALUE:
            raise exceptions.NoMatchingFunctionException(name)
        else:
            raise exceptions.NoMatchingMethodException(name, receiver)

    candidates2 = []
    lazy_params = None
    no_kwargs = None
    if receiver is not utils.NO_VALUE:
        args = (receiver,) + args
    for level in candidates:
        new_level = []
        for c in level:
            if no_kwargs is None:
                no_kwargs = c.no_kwargs
                args, kwargs = translate_args(no_kwargs, args, kwargs)
            elif no_kwargs != c.no_kwargs:
                raise_ambiguous()

            mapping = c.map_args(args, kwargs, context, engine)
            if mapping is None:
                continue
            pos, kwd = mapping
            lazy = set()
            for i, pos_arg in enumerate(pos):
                if isinstance(pos_arg.value_type, yaqltypes.LazyParameterType):
                    lazy.add(i)
            for key, value in kwd.items():
                if isinstance(value.value_type, yaqltypes.LazyParameterType):
                    lazy.add(key)
            if lazy_params is None:
                lazy_params = lazy
            elif lazy_params != lazy:
                raise_ambiguous()
            new_level.append((c, mapping))
        if new_level:
            candidates2.append(new_level)

    if len(candidates2) == 0:
        raise_not_found()

    arg_evaluator = lambda i, arg: (  # noqa: E731
        arg(utils.NO_VALUE, context, engine)
        if (i not in lazy_params and isinstance(arg, expressions.Expression)
            and not isinstance(arg, expressions.Constant))
        else arg
    )

    args = tuple(arg_evaluator(i, arg) for i, arg in enumerate(args))
    for key, value in kwargs.items():
        kwargs[key] = arg_evaluator(key, value)

    delegate = None
    winner_mapping = None
    for level in candidates2:
        for c, mapping in level:
            try:
                d = c.get_delegate(receiver, engine, context, args, kwargs)
            except exceptions.ArgumentException:
                pass
            else:
                if delegate is not None:
                    if _is_specialization_of(winner_mapping, mapping):
                        continue
                    elif not _is_specialization_of(mapping, winner_mapping):
                        raise_ambiguous()
                delegate = d
                winner_mapping = mapping
        if delegate is not None:
            break

    if delegate is None:
        raise_not_found()
    return lambda: delegate()


def translate_args(without_kwargs, args, kwargs):
    if without_kwargs:
        if len(kwargs) > 0:
            raise exceptions.ArgumentException(next(iter(kwargs)))
        return args, {}
    pos_args = []
    kw_args = {}
    for t in args:
        if isinstance(t, expressions.MappingRuleExpression):
            param_name = t.source
            if isinstance(param_name, expressions.KeywordConstant):
                param_name = param_name.value
            else:
                raise exceptions.MappingTranslationException()
            kw_args[param_name] = t.destination
        else:
            pos_args.append(t)
    for key, value in kwargs.items():
        if key in kw_args:
            raise exceptions.MappingTranslationException()
        else:
            kw_args[key] = value
    return tuple(pos_args), kw_args


def _is_specialization_of(mapping1, mapping2):
    args_mapping1, kwargs_mapping1 = mapping1
    args_mapping2, kwargs_mapping2 = mapping2
    res = False

    for a1, a2 in zip(args_mapping1, args_mapping2):
        if a2.value_type.is_specialization_of(a1.value_type):
            return False
        elif a1.value_type.is_specialization_of(a2.value_type):
            res = True

    for key, a1 in kwargs_mapping1.items():
        a2 = kwargs_mapping2[key]
        if a2.value_type.is_specialization_of(a1.value_type):
            return False
        elif a1.value_type.is_specialization_of(a2.value_type):
            res = True

    return res
