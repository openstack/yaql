#    Copyright (c) 2013 Mirantis, Inc.
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
from yaql.language.context import Context
from yaql.language.exceptions import (YaqlExecutionException,
                                      NoFunctionRegisteredException,
                                      YaqlException)
import yaql


class Expression(object):
    class Callable(object):
        def __init__(self, wrapped_object, context, key=None):
            self.wrapped_object = wrapped_object
            self.yaql_context = context
            self.key = key

        def __str__(self):
            return str(self.key)

    def evaluate(self, data=None, context=None):
        if not context:
            context = Context(yaql.create_context())
        if data:
            context.set_data(data)

        f = self.create_callable(context)
        # noinspection PyCallingNonCallable
        return f()

    def create_callable(self, context):
        pass


class Function(Expression):
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    class Callable(Expression.Callable):
        def __init__(self, wrapped, context, function_name, args):
            super(Function.Callable, self).__init__(wrapped, None,
                                                    key=function_name)
            self.function_name = function_name
            self.args = args
            self.yaql_context = context

        def __call__(self, *context_args, **context_kwargs):
            sender = context_kwargs.get('sender')

            if context_args:  # passed args have to be placed in the context
                self.yaql_context.set_data(context_args[0])
                for i, param in enumerate(context_args):
                    self.yaql_context.set_data(param, '$' + str(i + 1))
            for arg_name, arg_value in context_kwargs.items():
                self.yaql_context.set_data(arg_value, '$' + arg_name)

            num_args = len(self.args) + 1 if sender else len(self.args)

            fs = self.yaql_context.get_functions(self.function_name, num_args)
            if not fs:
                raise NoFunctionRegisteredException(self.function_name,
                                                    num_args)
            snapshot = self.yaql_context.take_snapshot()
            for func in fs:
                try:
                    result, res_context = func(self.yaql_context, sender,
                                               *self.args)
                    self.yaql_context = res_context
                    return result
                except YaqlExecutionException:
                    self.yaql_context.restore(snapshot)
                    continue
            raise YaqlException(
                "Registered function(s) matched but none"
                " could run successfully")

    def create_callable(self, context):
        return Function.Callable(self, context, self.name, self.args)


class BinaryOperator(Function):
    def __init__(self, op, obj1, obj2):
        super(BinaryOperator, self).__init__("operator_" + op, obj1,
                                             obj2)


class UnaryOperator(Function):
    def __init__(self, op, obj):
        super(UnaryOperator, self).__init__("unary_" + op, obj)


class Filter(Function):
    def __init__(self, value, expression):
        super(Filter, self).__init__("where", value, expression)


class Tuple(Function):
    def __init__(self, left, right):
        super(Tuple, self).__init__('tuple', left, right)

    @staticmethod
    def create_tuple(left, right):
        if isinstance(left, Tuple):
            new_args = list(left.args)
            new_args.append(right)
            left.args = tuple(new_args)
            return left
        else:
            return Tuple(left, right)


class Wrap(Function):
    def __init__(self, content):
        super(Wrap, self).__init__('wrap', content)


class GetContextValue(Function):
    def __init__(self, path):
        super(GetContextValue, self).__init__("get_context_data", path)
        self.path = path

    def __str__(self):
        return self.path


class Constant(Expression):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    class Callable(Expression.Callable):
        def __init__(self, wrapped, value, context):
            super(Constant.Callable, self).__init__(wrapped, context,
                                                    key=value)
            self.value = value

        # noinspection PyUnusedLocal
        def __call__(self, *args):
            return self.value

    def create_callable(self, context):
        return Constant.Callable(self, self.value, context)


def pre_process_args(func, args):
    res = list(args)
    if hasattr(func, 'arg_requirements'):
        if hasattr(func, 'is_context_aware'):
            ca = func.context_aware
            att_map = ca.map_args(args)
        else:
            att_map = {}
            arg_names = inspect.getargspec(func).args
            for i, arg_name in enumerate(arg_names):
                att_map[arg_name] = args[i]
        for arg_name in func.arg_requirements:
            arg_func = att_map[arg_name]
            if func.arg_requirements[arg_name].eval_arg:
                try:
                    arg_val = arg_func()
                except:
                    raise YaqlExecutionException(
                        "Unable to evaluate argument {0}".format(arg_name))
            else:
                arg_val = arg_func

            if func.arg_requirements[arg_name].constant_only:
                if not isinstance(arg_func, Constant.Callable):
                    raise YaqlExecutionException(
                        "{0} needs to be a constant".format(arg_name))
            if func.arg_requirements[arg_name].function_only:
                if not isinstance(arg_func, Function.Callable):
                    raise YaqlExecutionException(
                        "{0} needs to be a function".format(arg_name))

            arg_type = func.arg_requirements[arg_name].arg_type
            custom_validator = func.arg_requirements[arg_name].custom_validator
            ok = True
            if arg_type:
                ok = ok and isinstance(arg_val, arg_type)
                if type(arg_val) == types.BooleanType:
                    ok = ok and type(arg_val) == arg_type
            if custom_validator:
                ok = ok and custom_validator(arg_val)

            if not ok:
                raise YaqlExecutionException(
                    "Argument {0} is invalid".format(arg_name))
            res[args.index(arg_func)] = arg_val

    return res
