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
from functools import wraps
import inspect
import types
from yaql.exceptions import NoArgumentFound
from yaql.exceptions import DuplicateArgumentDecoratorException
from yaql.exceptions import YaqlExecutionException
from yaql.exceptions import DuplicateContextDecoratorException
from yaql.expressions import Expression
from yaql.expressions import Constant
from yaql.expressions import Function


class ArgDef(object):
    def __init__(self,
                 arg_name,
                 eval=False,
                 type=None,
                 custom_validator=None,
                 constant_only=False,
                 function_only=False,
                 is_context=False,
                 is_self=False,
                 inverse_context=False):
        self.arg_name = arg_name
        self.eval = eval
        self.type = type
        self.custom_validator = custom_validator
        self.constant_only = constant_only
        self.function_only = function_only
        self.is_context = is_context
        self.is_self = is_self
        self.inverse_context = inverse_context

    def validate(self, arg):
        if self.constant_only:
            if not isinstance(arg, Constant.Callable):
                raise YaqlExecutionException(
                    "{0} has to be a constant".format(self.arg_name))

        if self.function_only:
            if not isinstance(arg, Function.Callable):
                raise YaqlExecutionException(
                    "{0} has to be a function".format(self.arg_name))

        if self.eval:
            if not isinstance(arg, Expression.Callable):
                raise YaqlExecutionException(
                    "{0} has to be Callable Expression to be evaluated".format(
                        self.arg_name))
            try:
                val = arg()
            except:
                raise YaqlExecutionException(
                    "Unable to evaluate argument {0}".format(self.arg_name))
        else:
            val = arg

        ok = True
        if self.type:
            if isinstance(val, types.BooleanType):
                ok = ok and self.type is types.BooleanType
            else:
                ok = ok and isinstance(val, self.type)
        if self.custom_validator:
            try:
                ok = ok and self.custom_validator(val)
            except:
                raise YaqlExecutionException(
                    "Unable to validated argument {0}".format(self.arg_name))
        if not ok:
                raise YaqlExecutionException(
                    "Argument {0} is invalid".format(self.arg_name))
        return val



def _validate_func(self, self_data, *args):
    i = 0
    for arg_rule in self.func_arg_rules.values():
        if arg_rule.is_context:
            continue


def _attach_arg_data(func, arg):
    if not hasattr(func, 'func_arg_rules'):
        func.func_arg_rules = {}
    if not hasattr(func, 'func_arg_validate'):
        func.func_arg_validate = _validate_func
    if arg.arg_name in func.func_arg_rules:
        raise DuplicateArgumentDecoratorException(func.__name__, arg.arg_name)

    if arg.is_context:
        if hasattr(func, 'func_is_context_aware') and \
                func.func_is_context_aware:
            raise DuplicateContextDecoratorException(func.__name__)
        func.func_is_context_aware = True

    func.func_arg_rules[arg.arg_name] = arg
    return func


def argument(arg_name,
             eval=False,
             type=None,
             custom_validator=None,
             constant_only=False,
             function_only=False,
             is_context=False,
             is_self=False,
             inverse_context=False):
    def get_wrapper(func):
        return _attach_arg_data(func,
                                ArgDef(arg_name, eval, type, custom_validator,
                                       constant_only, function_only,
                                       is_context,
                                       is_self, inverse_context))

    return get_wrapper


def context_aware(arg=None):
    if callable(arg):  # no-arg decorator case
        return _attach_arg_data(arg, ArgDef('context', is_context=True))
    else:
        return argument(arg, is_context=True)


class arg(object):
    def __init__(self, arg_name, type=None, custom_validator=None,
                 constant_only=False, function_only=False, eval_arg=True):
        self.arg_name = arg_name
        self.arg_type = type
        self.custom_validator = custom_validator
        self.constant_only = constant_only
        self.function_only = function_only
        self.eval_arg = eval_arg

    def __call__(self, function):
        if getattr(function, 'is_context_aware', False):
            real_args = function.context_aware.real_args
        else:
            real_args = inspect.getargspec(function).args
        if not self.arg_name in real_args:
            raise NoArgumentFound(function.__name__,
                                  self.arg_name)
        if not hasattr(function, 'arg_requirements'):
            function.arg_requirements = {self.arg_name: self}
        else:
            function.arg_requirements[self.arg_name] = self
        return function


class ContextAware(object):
    def __init__(self, context_parameter_name='context'):
        self.context_parameter_name = context_parameter_name

    def map_args(self, arg_list):
        res = {}
        i = 0
        for real_arg in getattr(self, 'real_args', []):
            if real_arg != self.context_parameter_name:
                res[real_arg] = arg_list[i]
                i += 1
        return res

    def get_num_callable_args(self):
        return len(self.real_args) - 1

    def __call__(self, function):
        @wraps(function)
        def context_aware_function(context, *args):
            real_args = inspect.getargspec(function).args
            if not self.context_parameter_name in real_args:
                raise NoArgumentFound(function.__name__,
                                      self.context_parameter_name)
            index = real_args.index(self.context_parameter_name)
            args_to_pass = list(args)
            args_to_pass.insert(index, context)
            return function(*args_to_pass)

        argspec = inspect.getargspec(function)
        self.varargs = argspec.varargs
        self.kwargs = argspec.keywords
        self.real_args = argspec.args
        f = context_aware_function
        f.is_context_aware = True
        f.context_aware = self
        return f
