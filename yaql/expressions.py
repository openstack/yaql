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

import types
from context import *
from exceptions import YaqlExecutionException, NoFunctionRegisteredException
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
            self.obj_wrapper = None

        def __call__(self, *f_params):
            args_to_pass = []
            if f_params:
                if len(f_params) == 1 and isinstance(f_params[0],
                                                     Expression.Callable):
                    self.obj_wrapper = f_params[0]
                    self.yaql_context = Context(self.obj_wrapper.yaql_context)
                else:
                    param_context = self._find_param_context()
                    param_context.set_data(f_params[0])
                    for i in range(0, len(f_params)):
                        param_context.set_data(f_params[i], '$' + str(i + 1))
            if self.obj_wrapper:
                args_to_pass.append(self.obj_wrapper)
            for arg in self.args:
                argContext = Context(self.yaql_context)
                wrapped_arg = arg.create_callable(argContext)
                args_to_pass.append(wrapped_arg)

            numArg = len(args_to_pass)
            fs = self.yaql_context.get_functions(self.function_name, numArg)
            if not fs:
                raise NoFunctionRegisteredException(self.function_name, numArg)
            for func in fs:
                try:
                    processed_args = pre_process_args(func, args_to_pass)
                    if hasattr(func, "is_context_aware"):
                        return func(self.yaql_context, *processed_args)
                    else:
                        return func(*processed_args)
                except YaqlExecutionException:
                    continue
            raise YaqlExecutionException("Unable to run " + self.function_name)

        def _find_param_context(self):
            context = self.yaql_context
            wrapper = self.obj_wrapper
            while wrapper:
                context = wrapper.yaql_context
                wrapper = getattr(wrapper, 'obj_wrapper', None)
            return context

    def create_callable(self, context):
        return Function.Callable(self, context, self.name, self.args)


class BinaryOperator(Function):
    def __init__(self, op, obj1, obj2):
        super(BinaryOperator, self).__init__("operator_" + op, obj1,
                                             obj2)


class UnaryOperator(Function):
    def __init__(self, op, obj):
        super(UnaryOperator, self).__init__("operator_" + op, obj)


class Filter(Function):
    def __init__(self, expression):
        super(Filter, self).__init__("where", expression)


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
        def __init__(self, wrapped, value):
            super(Constant.Callable, self).__init__(wrapped, None, key=value)
            self.value = value

        # noinspection PyUnusedLocal
        def __call__(self, *args):
            return self.value

    def create_callable(self, context):
        return Constant.Callable(self, self.value)


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
