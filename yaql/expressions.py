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
        def __init__(self, wrapped_object, context):
            self.wrapped_object = wrapped_object
            self.yaql_context = context

    def evaluate(self, data=None, context=None):
        if not context:
            context = Context(yaql.create_context())
        if data is not None:
            context.set_data(data)

        f = self.create_callable(context)
        # noinspection PyCallingNonCallable
        return f()

    def create_callable(self, context):
        pass


class Function(Expression):
    def __init__(self, name, obj, *args):
        self.name = name
        self.object = obj
        self.args = args

    class Callable(Expression.Callable):
        def __init__(self, wrapped, context, function_name, obj, args):
            super(Function.Callable, self).__init__(wrapped, None)
            self.function_name = function_name
            self.obj = obj
            self.args = args
            if obj:
                self.obj_wrapper = self.obj.create_callable(context)
                if self.obj_wrapper.yaql_context:
                    self.yaql_context = Context(self.obj_wrapper.yaql_context)
                else:
                    self.yaql_context = context
            else:
                self.yaql_context = context
                self.obj_wrapper = None

        def __call__(self, *f_params):
            args_to_pass = []
            context = self.yaql_context
            if f_params:
                param_context = self._find_param_context()
                param_context.set_data(f_params[0])
                for i in range(0, len(f_params)):
                    param_context.set_data(f_params[i], '$' + str(i + 1))
            this = None
            if self.obj_wrapper:
                this = self.obj_wrapper()
                args_to_pass.append(lambda: this)
            for arg in self.args:
                argContext = Context(context)
                wrapped_arg = arg.create_callable(argContext)
                args_to_pass.append(wrapped_arg)

            numArg = len(args_to_pass)
            fs = []

            if not self.function_name.startswith('#'):
                resolvers = self.yaql_context.get_functions('#resolve', 2)
                if resolvers:
                    try:
                        fs = self._try_invoke(
                            resolvers,
                            [self.function_name, this], context) or []
                        if not isinstance(fs, types.ListType):
                            fs = [fs]
                    except YaqlExecutionException:
                        fs = []

            fs.extend(self.yaql_context.get_functions(
                self.function_name, numArg))
            if not fs:
                raise NoFunctionRegisteredException(self.function_name, numArg)
            try:
                return self._try_invoke(fs, args_to_pass, context)
            except YaqlExecutionException:
                raise YaqlExecutionException(
                    'Unable to run ' + self.function_name)

        def _try_invoke(self, funcs, args, context):
            for func in funcs:
                try:
                    args_to_pass = pre_process_args(func, args)
                    if hasattr(func, 'is_context_aware'):
                        return func(context, *args_to_pass)
                    else:
                        return func(*args_to_pass)
                except YaqlExecutionException:
                    continue
            raise YaqlExecutionException()


        def _find_param_context(self):
            context = self.yaql_context
            wrapper = self.obj_wrapper
            while wrapper:
                context = wrapper.yaql_context
                wrapper = getattr(wrapper, 'obj_wrapper', None)
            return context


    def create_callable(self, context):
        return Function.Callable(self, context, self.name, self.object,
                                 self.args)


class BinaryOperator(Function):
    def __init__(self, op, obj1, obj2):
        super(BinaryOperator, self).__init__("#operator_" + op, None, obj1,
                                             obj2)


class UnaryOperator(Function):
    def __init__(self, op, obj):
        super(UnaryOperator, self).__init__("#operator_" + op, obj)


class Att(Function):
    def __init__(self, obj, att):
        super(Att, self).__init__('#operator_.', obj, att)


class Filter(Function):
    def __init__(self, obj, expression):
        super(Filter, self).__init__("where", obj, expression)


class Tuple(Function):
    def __init__(self, left, right):
        super(Tuple, self).__init__('tuple', None, left, right)

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
        super(Wrap, self).__init__('#wrap', None, content)


class GetContextValue(Function):
    def __init__(self, path):
        super(GetContextValue, self).__init__("#get_context_data", None,
                                              path)
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
            super(Constant.Callable, self).__init__(wrapped, None)
            self.value = value

        # noinspection PyUnusedLocal
        def __call__(self, *args):
            return self.value

    def create_callable(self, context):
        return Constant.Callable(self, self.value)


def pre_process_args(func, args):
    result = args[:]
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
            try:
                arg_val = arg_func()
            except:
                raise YaqlExecutionException(
                    "Unable to evaluate argument {0}".format(arg_name))
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
            result[args.index(arg_func)] = arg_val

    return tuple(result)
