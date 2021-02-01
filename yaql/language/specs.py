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

from yaql.language import exceptions
from yaql.language import utils
from yaql.language import yaqltypes

NO_DEFAULT = utils.create_marker('<NoValue>')


class ParameterDefinition(object):
    __slots__ = ('value_type', 'name', 'position', 'default', 'alias')

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
    __slots__ = ('is_method', 'is_function', 'name', 'parameters', 'payload',
                 'doc', 'no_kwargs', 'meta')

    def __init__(self, name, payload, parameters=None, doc='', meta=None,
                 is_function=True, is_method=False, no_kwargs=False):
        self.is_method = is_method
        self.is_function = is_function
        self.name = name
        self.parameters = {} if not parameters else parameters
        self.payload = payload
        self.doc = doc
        self.no_kwargs = no_kwargs
        self.meta = meta or {}

    def __call__(self, engine, context, receiver=utils.NO_VALUE):
        def func(*args, **kwargs):
            if receiver is not utils.NO_VALUE:
                args = (receiver,) + args
            return self.get_delegate(receiver, engine, context, args, kwargs)()
        return func

    def clone(self):
        parameters = {key: p.clone() for key, p in self.parameters.items()}

        res = FunctionDefinition(
            self.name, self.payload, parameters, self.doc,
            self.meta, self.is_function, self.is_method, self.no_kwargs)
        return res

    def strip_hidden_parameters(self):
        fd = self.clone()
        keys_to_remove = set()

        for k, v in fd.parameters.items():
            if not isinstance(v.value_type, yaqltypes.HiddenParameterType):
                continue
            keys_to_remove.add(k)
            if v.position is not None:
                for v2 in fd.parameters.values():
                    if v2.position is not None and v2.position > v.position:
                        v2.position -= 1
        for key in keys_to_remove:
            del fd.parameters[key]
        return fd

    def set_parameter(self, name, value_type=None, nullable=None,
                      alias=None, overwrite=False):
        if isinstance(name, ParameterDefinition):
            if name.name in self.parameters and not overwrite:
                raise exceptions.DuplicateParameterDecoratorException(
                    function_name=self.name or self.payload.__name__,
                    param_name=name.name)
            self.parameters[name.name] = name
            return name

        spec = inspect.getfullargspec(self.payload)
        if isinstance(name, int):
            if 0 <= name < len(spec.args):
                name = spec.args[name]
            elif name == len(spec.args) and spec.varargs is not None:
                name = spec.varargs
            else:
                raise IndexError('argument position is out of range')

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
                function_name=self.name or self.payload.__name__,
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

        if arg_name in self.parameters and not overwrite:
            raise exceptions.DuplicateParameterDecoratorException(
                function_name=self.name or self.payload.__name__,
                param_name=name)

        yaql_type = value_type
        p_nullable = nullable
        if value_type is None:
            if p_nullable is None:
                p_nullable = True
            base_type = object \
                if default in (None, NO_DEFAULT, utils.NO_VALUE) \
                else type(default)
            yaql_type = yaqltypes.PythonType(base_type, p_nullable)
        elif not isinstance(value_type, yaqltypes.SmartType):
            if p_nullable is None:
                p_nullable = default is None
            yaql_type = yaqltypes.PythonType(value_type, p_nullable)

        pd = ParameterDefinition(
            name, yaql_type, position, alias, default
        )
        self.parameters[arg_name] = pd
        return pd

    def insert_parameter(self, name, value_type=None, nullable=None,
                         alias=None, overwrite=False):
        pd = self.set_parameter(name, value_type, nullable, alias, overwrite)
        for p in self.parameters.values():
            if p is pd:
                continue
            if p.position is not None and p.position >= pd.position:
                p.position += 1

    def map_args(self, args, kwargs, context, engine):
        kwargs = dict(kwargs)
        positional_args = len(args) * [
            self.parameters.get('*', utils.NO_VALUE)]
        max_dst_positional_args = len(args) + len(self.parameters)
        positional_fix_table = max_dst_positional_args * [0]
        keyword_args = {}

        for p in self.parameters.values():
            if p.position is not None and isinstance(
                    p.value_type, yaqltypes.HiddenParameterType):
                for index in range(p.position + 1, len(positional_fix_table)):
                    positional_fix_table[index] += 1

        for key, p in self.parameters.items():
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
                for key in kwargs:
                    keyword_args[key] = argdef
            else:
                return None

        for i in range(len(positional_args)):
            if positional_args[i] is utils.NO_VALUE:
                return None
            value = args[i]
            if value is utils.NO_VALUE:
                value = positional_args[i].default
            if not positional_args[i].value_type.check(value, context, engine):
                return None
        for kwd in kwargs:
            if not keyword_args[kwd].value_type.check(
                    kwargs[kwd], context, engine):
                return None

        return tuple(positional_args), keyword_args

    def get_delegate(self, receiver, engine, context, args, kwargs):
        def checked(val, param):
            if not param.value_type.check(val, context, engine):
                raise exceptions.ArgumentException(param.name)

            def convert_arg_func(context2):
                try:
                    return param.value_type.convert(
                        val, receiver, context2, self, engine)
                except exceptions.ArgumentValueException:
                    raise exceptions.ArgumentException(param.name)
            return convert_arg_func

        kwargs = kwargs.copy()
        kwargs = dict(kwargs)
        positional = 0
        for arg_name, p in self.parameters.items():
            if p.position is not None and arg_name != '*':
                positional += 1

        positional_args = positional * [None]
        positional_fix_table = positional * [0]
        keyword_args = {}

        for p in self.parameters.values():
            if p.position is not None and isinstance(
                    p.value_type, yaqltypes.HiddenParameterType):
                for index in range(p.position + 1, positional):
                    positional_fix_table[index] += 1

        for key, p in self.parameters.items():
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
                for key, value in kwargs.items():
                    keyword_args[key] = checked(value, argdef)
            else:
                raise exceptions.ArgumentException('**')

        def func():
            new_context = context.create_child_context()
            result = self.payload(
                *tuple(map(lambda t: t(new_context),
                           positional_args)),
                **dict(map(lambda t: (t[0], t[1](new_context)),
                           keyword_args.items()))
            )
            return result

        return func

    def is_valid_method(self):
        min_position = len(self.parameters)
        min_arg = None
        for p in self.parameters.values():
            if p.position is not None and p.position < min_position and \
                    not isinstance(p.value_type,
                                   yaqltypes.HiddenParameterType):
                min_position = p.position
                min_arg = p
        return min_arg and not isinstance(
            min_arg.value_type, yaqltypes.LazyParameterType)


def _get_function_definition(func):
    if not hasattr(func, '__yaql_function__'):
        fd = FunctionDefinition(None, func, {}, func.__doc__)
        func.__yaql_function__ = fd
    return func.__yaql_function__


def _infer_parameter_type(name):
    if name == 'context' or name == '__context':
        return yaqltypes.Context()
    elif name == 'engine' or name == '__engine':
        return yaqltypes.Engine()
    elif name == 'yaql_interface' or name == '__yaql_interface':
        return yaqltypes.YaqlInterface()


def convert_function_name(function_name, convention):
    if not function_name:
        return function_name
    function_name = function_name.rstrip('_')
    if not convention:
        return function_name
    if not function_name[0].isalpha():
        finish = function_name.find(function_name[0], 1)
        if finish <= 1:
            return function_name
        return function_name[:finish + 1] + convention.convert_function_name(
            function_name[finish + 1:])
    return convention.convert_function_name(function_name)


def convert_parameter_name(parameter_name, convention):
    if not parameter_name:
        return parameter_name
    parameter_name = parameter_name.rstrip('_')
    if not convention:
        return parameter_name
    return convention.convert_parameter_name(parameter_name)


def get_function_definition(func, name=None, function=None, method=None,
                            convention=None, parameter_type_func=None):
    if parameter_type_func is None:
        parameter_type_func = _infer_parameter_type
    fd = _get_function_definition(func).clone()
    spec = inspect.getfullargspec(func)
    for arg in spec.args + spec.kwonlyargs:
        if arg not in fd.parameters:
            fd.set_parameter(arg, parameter_type_func(arg))
    if spec.varargs and '*' not in fd.parameters:
        fd.set_parameter(spec.varargs, parameter_type_func(spec.varargs))
    if spec.varkw and '**' not in fd.parameters:
        fd.set_parameter(spec.varkw, parameter_type_func(spec.varkw))

    if name is not None:
        fd.name = name
    elif fd.name is None:
        fd.name = convert_function_name(fd.payload.__name__, convention)
    elif convention is not None:
        fd.name = convert_function_name(fd.name, convention)

    if function is not None:
        fd.is_function = function
    if method is not None:
        fd.is_method = method
    if convention:
        for p in fd.parameters.values():
            if p.alias is None:
                p.alias = convert_parameter_name(p.name, convention)
    return fd


def _parameter(name, value_type=None, nullable=None, alias=None):
    def wrapper(func):
        fd = _get_function_definition(func)
        fd.set_parameter(name, value_type, nullable, alias)
        return func
    return wrapper


def parameter(name, value_type=None, nullable=None, alias=None):
    if value_type is not None and isinstance(
            value_type, yaqltypes.HiddenParameterType):
        raise ValueError('Use inject() for hidden parameters')
    return _parameter(name, value_type, nullable=nullable, alias=alias)


def inject(name, value_type=None, nullable=None, alias=None):
    if value_type is not None and not isinstance(
            value_type, yaqltypes.HiddenParameterType):
        raise ValueError('Use parameter() for normal function parameters')
    return _parameter(name, value_type, nullable=nullable, alias=alias)


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


def no_kwargs(func):
    fd = _get_function_definition(func)
    fd.no_kwargs = True
    return func


def meta(name, value):
    def wrapper(func):
        fd = _get_function_definition(func)
        fd.meta[name] = value
        return func
    return wrapper


def yaql_property(source_type):
    def decorator(func):
        @name('#property#{0}'.format(get_function_definition(func).name))
        @parameter('obj', source_type)
        def wrapper(obj):
            return func(obj)
        return wrapper
    return decorator
