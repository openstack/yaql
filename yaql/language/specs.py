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

import inspect
import types

import six

from yaql.language import exceptions
from yaql.language import utils
from yaql.language import yaqltypes

NO_DEFAULT = utils.create_marker('<NoValue>')


class ParameterDefinition(object):
    def __init__(self, name, value_type=None, position=None, alias=None,
                 default=None):
        self.value_type = value_type
        self.name = name
        self.position = position
        self.default = default
        self.alias = alias

    def __repr__(self):
        return '{0} => position={1} value_type={2} default={3}'.format(
            self.name, self.position, self.value_type, self.default)

    def clone(self):
        return ParameterDefinition(self.name, self.value_type,
                                   self.position, self.alias, self.default)


class FunctionDefinition(object):
    def __init__(self, name, parameters, payload, doc='',
                 is_function=True, is_method=False,
                 returns_context=False, no_kwargs=False):
        self.is_method = is_method
        self.is_function = is_function
        self.name = name
        self.parameters = parameters
        self.payload = payload
        self.doc = doc
        self.returns_context = returns_context
        self.no_kwargs = no_kwargs

    def __call__(self, sender, engine, context):
        return lambda *args, **kwargs: \
            self.get_delegate(sender, engine, args, kwargs)(context)[0]

    def clone(self):
        parameters = dict(
            (key, p.clone())
            for key, p in six.iteritems(self.parameters))

        res = FunctionDefinition(
            self.name, parameters, self.payload,
            self.doc, self.is_function, self.is_method,
            self.returns_context, self.no_kwargs)
        return res

    def map_args(self, args, kwargs):
        kwargs = dict(kwargs)
        positional_args = len(args) * [
            self.parameters.get('*', utils.NO_VALUE)]
        max_dst_positional_args = len(args) + len(self.parameters)
        positional_fix_table = max_dst_positional_args * [0]
        keyword_args = {}

        for p in six.itervalues(self.parameters):
            if p.position is not None and isinstance(
                    p.value_type, yaqltypes.HiddenParameterType):
                for index in range(p.position + 1, len(positional_fix_table)):
                    positional_fix_table[index] += 1

        for key, p in six.iteritems(self.parameters):
            arg_name = p.alias or p.name
            if p.position is not None and key != '*':
                arg_position = p.position - positional_fix_table[p.position]
                if isinstance(p.value_type, yaqltypes.HiddenParameterType):
                    continue
                elif arg_position < len(args) and args[arg_position] \
                        is not utils.NO_VALUE:
                    if arg_name in kwargs:
                        return None
                    positional_args[arg_position] = p
                elif arg_name in kwargs:
                    keyword_args[arg_name] = p
                    del kwargs[arg_name]
                elif p.default is NO_DEFAULT:
                    return None
                elif arg_position < len(args) and args[arg_position]:
                    positional_args[arg_position] = p

            elif p.position is None and key != '**':
                if isinstance(p.value_type, yaqltypes.HiddenParameterType):
                    continue
                elif arg_name in kwargs:
                    keyword_args[arg_name] = p
                    del kwargs[arg_name]
                elif p.default is NO_DEFAULT:
                    return None

        if len(kwargs) > 0:
            if '**' in self.parameters:
                argdef = self.parameters['**']
                for key in six.iterkeys(kwargs):
                    keyword_args[key] = argdef
            else:
                return None

        for i in range(len(positional_args)):
            if positional_args[i] is utils.NO_VALUE:
                return None
            value = args[i]
            if value is utils.NO_VALUE:
                value = positional_args[i].default
            if not positional_args[i].value_type.check(value):
                return None
        for kwd in six.iterkeys(kwargs):
            if not keyword_args[kwd].value_type.check(kwargs[kwd]):
                return None

        return tuple(positional_args), keyword_args

    def get_delegate(self, sender, engine, args, kwargs):
        def checked(val, param):
            if not param.value_type.check(val):
                raise exceptions.ArgumentException(param.name)

            def convert_arg_func(context):
                try:
                    return param.value_type.convert(
                        val, sender, context, self, engine)
                except exceptions.ArgumentValueException:
                    raise exceptions.ArgumentException(param.name)
            return convert_arg_func

        positional = 0
        for arg_name, p in six.iteritems(self.parameters):
            if p.position is not None and arg_name != '*':
                positional += 1

        positional_args = positional * [None]
        positional_fix_table = positional * [0]
        keyword_args = {}

        for p in six.itervalues(self.parameters):
            if p.position is not None and isinstance(
                    p.value_type, yaqltypes.HiddenParameterType):
                for index in range(p.position + 1, positional):
                    positional_fix_table[index] += 1

        for key, p in six.iteritems(self.parameters):
            arg_name = p.alias or p.name
            if p.position is not None and key != '*':
                if isinstance(p.value_type, yaqltypes.HiddenParameterType):
                    positional_args[p.position] = checked(None, p)
                    positional -= 1
                elif p.position - positional_fix_table[p.position] < len(
                        args) and args[p.position - positional_fix_table[
                            p.position]] is not utils.NO_VALUE:
                    if arg_name in kwargs:
                        raise exceptions.ArgumentException(p.name)
                    positional_args[p.position] = checked(
                        args[p.position - positional_fix_table[
                            p.position]], p)
                elif arg_name in kwargs:
                    positional_args[p.position] = checked(
                        kwargs.pop(arg_name), p)
                elif p.default is not NO_DEFAULT:
                    positional_args[p.position] = checked(p.default, p)
                else:
                    raise exceptions.ArgumentException(p.name)
            elif p.position is None and key != '**':
                if isinstance(p.value_type, yaqltypes.HiddenParameterType):
                    keyword_args[key] = checked(None, p)
                elif arg_name in kwargs:
                    keyword_args[key] = checked(kwargs.pop(arg_name), p)
                elif p.default is not NO_DEFAULT:
                    keyword_args[key] = checked(p.default, p)
                else:
                    raise exceptions.ArgumentException(p.name)
        if len(args) > positional:
            if '*' in self.parameters:
                argdef = self.parameters['*']
                positional_args.extend(
                    map(lambda t: checked(t, argdef), args[positional:]))
            else:
                raise exceptions.ArgumentException('*')
        if len(kwargs) > 0:
            if '**' in self.parameters:
                argdef = self.parameters['**']
                for key, value in six.iteritems(kwargs):
                    keyword_args[key] = checked(value, argdef)
            else:
                raise exceptions.ArgumentException('**')

        def func(context):
            new_context = context.create_child_context()
            result = self.payload(
                *tuple(map(lambda t: t(new_context),
                           positional_args)),
                **dict(map(lambda t: (t[0], t[1](new_context)),
                           six.iteritems(keyword_args)))
            )
            if self.returns_context:
                if isinstance(result, types.GeneratorType):
                    result_context = next(result)
                    return result, result_context
                result_value, result_context = result
                return result_value, result_context
            else:
                return result, new_context

        return func

    def is_valid_method(self):
        min_position = len(self.parameters)
        min_arg = None
        for p in six.itervalues(self.parameters):
            if p.position is not None and p.position < min_position and \
                    not isinstance(p.value_type,
                                   yaqltypes.HiddenParameterType):
                min_position = p.position
                min_arg = p
        return min_arg and not isinstance(
            min_arg.value_type, yaqltypes.LazyParameterType)


def _get_function_definition(func):
    if not hasattr(func, '__yaql_function__'):
        fd = FunctionDefinition(None, {}, func, func.__doc__)
        func.__yaql_function__ = fd
    return func.__yaql_function__


def get_function_definition(func, name=None, function=None, method=None,
                            convention=None):
    fd = _get_function_definition(func).clone()
    if six.PY2:
        spec = inspect.getargspec(func)
        for arg in spec.args:
            if arg not in fd.parameters:
                parameter(arg, function_definition=fd)(func)
        if spec.varargs and '*' not in fd.parameters:
            parameter(spec.varargs, function_definition=fd)(func)
        if spec.keywords and '**' not in fd.parameters:
            parameter(spec.keywords, function_definition=fd)(func)
    else:
        spec = inspect.getfullargspec(func)
        for arg in spec.args + spec.kwonlyargs:
            if arg not in fd.parameters:
                parameter(arg, function_definition=fd)(func)
        if spec.varargs and '*' not in fd.parameters:
            parameter(spec.varargs, function_definition=fd)(func)
        if spec.varkw and '**' not in fd.parameters:
            parameter(spec.varkw, function_definition=fd)(func)

    if name is not None:
        fd.name = name
    elif fd.name is None:
        if convention is not None:
            fd.name = convention.convert_function_name(fd.payload.__name__)
        else:
            fd.name = fd.payload.__name__
    if function is not None:
        fd.is_function = function
    if method is not None:
        fd.is_method = method
    if convention:
        for p in six.itervalues(fd.parameters):
            if p.alias is None:
                p.alias = convention.convert_parameter_name(p.name)

    return fd


def _parameter(name, value_type=None, nullable=None, alias=None,
               function_definition=None):
    def wrapper(func):
        fd = function_definition or _get_function_definition(func)
        if six.PY2:
            spec = inspect.getargspec(func)
            arg_name = name
            if name == spec.keywords:
                position = None
                arg_name = '**'
            elif name == spec.varargs:
                position = len(spec.args)
                arg_name = '*'
            elif name not in spec.args:
                raise exceptions.NoParameterFoundException(
                    function_name=fd.name or func.__name__,
                    param_name=name)
            else:
                position = spec.args.index(name)
            default = NO_DEFAULT
            if spec.defaults is not None and name in spec.args:
                index = spec.args.index(name) - len(spec.args)
                if index >= -len(spec.defaults):
                    default = spec.defaults[index]
        else:
            spec = inspect.getfullargspec(func)
            arg_name = name
            if name == spec.varkw:
                position = None
                arg_name = '**'
            elif name == spec.varargs:
                position = len(spec.args)
                arg_name = '*'
            elif name in spec.kwonlyargs:
                position = None
            elif name not in spec.args:
                raise exceptions.NoParameterFoundException(
                    function_name=fd.name or func.__name__,
                    param_name=name)
            else:
                position = spec.args.index(name)

            default = NO_DEFAULT
            if spec.defaults is not None and name in spec.args:
                index = spec.args.index(name) - len(spec.args)
                if index >= -len(spec.defaults):
                    default = spec.defaults[index]
            elif spec.kwonlydefaults is not None:
                default = spec.kwonlydefaults.get(name, NO_DEFAULT)

        if arg_name in fd.parameters:
            raise exceptions.DuplicateParameterDecoratorException(
                function_name=fd.name or func.__name__,
                param_name=name)

        yaql_type = value_type
        p_nullable = nullable
        if value_type is None:
            if p_nullable is None:
                p_nullable = True
            if name == 'context':
                yaql_type = yaqltypes.Context()
            elif name == 'engine':
                yaql_type = yaqltypes.Engine()
            else:
                base_type = object \
                    if default in (None, NO_DEFAULT, utils.NO_VALUE) \
                    else type(default)
                yaql_type = yaqltypes.PythonType(base_type, p_nullable)
        elif not isinstance(value_type, yaqltypes.SmartType):
            if p_nullable is None:
                p_nullable = default is None
            yaql_type = yaqltypes.PythonType(value_type, p_nullable)

        fd.parameters[arg_name] = ParameterDefinition(
            name, yaql_type, position, alias, default
        )

        return func
    return wrapper


def parameter(name, value_type=None, nullable=None, alias=None,
              function_definition=None):
    if value_type is not None and isinstance(
            value_type, yaqltypes.HiddenParameterType):
        raise ValueError('Use inject() for hidden parameters')
    return _parameter(name, value_type, nullable=nullable, alias=alias,
                      function_definition=function_definition)


def inject(name, value_type=None, nullable=None, alias=None,
           function_definition=None):
    if value_type is not None and not isinstance(
            value_type, yaqltypes.HiddenParameterType):
        raise ValueError('Use parameter() for normal function parameters')
    return _parameter(name, value_type, nullable=nullable, alias=alias,
                      function_definition=function_definition)


def name(function_name):
    def wrapper(func):
        fd = _get_function_definition(func)
        fd.name = function_name
        return func
    return wrapper


def method(func):
    fd = _get_function_definition(func)
    fd.is_method = True
    fd.is_function = False
    return func


def extension_method(func):
    fd = _get_function_definition(func)
    fd.is_method = True
    fd.is_function = True
    return func


def returns_context(func):
    fd = _get_function_definition(func)
    fd.returns_context = True
    return func


def no_kwargs(func):
    fd = _get_function_definition(func)
    fd.no_kwargs = True
    return func
