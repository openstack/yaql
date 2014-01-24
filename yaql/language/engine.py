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
import inspect
import types
import sys

from yaql.language.exceptions import *
import yaql.language.context

import yaql.language.expressions


def yaql_function(function):
    if not hasattr(function, "__yaql__"):
        if isinstance(function, types.MethodType):
            function = function.im_func
        function.__yaql__ = YaqlFunctionDefinition(function)
    return function.__yaql__


class YaqlFunctionDefinition(object):
    def __init__(self, function):
        self.function = function
        self.is_context_aware = False
        self.context_param_name = None
        self.self_param_name = None
        self.context_owner_param_name = None
        self.param_definitions = {}
        self._arg_spec = inspect.getargspec(function)
        self._inverse_context = False
        if self._arg_spec.keywords:
            raise YaqlException("Keyword parameters are not supported")

    def register_param_constraint(self, param):
        if param.name not in self._arg_spec.args \
            and self._arg_spec.varargs != param.name:
            raise NoParameterFoundException(
                function_name=self.function.func_name,
                param_name=param.name)
        if param.name in self.param_definitions:
            raise DuplicateParameterDecoratorException(
                function_name=self.function.func_name,
                param_name=param.name)
        if self.is_context_aware and param.is_context:
            raise DuplicateContextDecoratorException(
                function_name=self.function.func_name)
        if self.context_owner_param_name and param.own_context:
            raise DuplicateContextOwnerDecoratorException(
                function_name=self.function.func_name)
        self.param_definitions[param.name] = param
        if param.is_context:
            self.is_context_aware = True
            self.context_param_name = param.name
        if param.is_self is None:
            if param.name in self._arg_spec.args:
                param.is_self = self._arg_spec.args.index(
                    param.name) == 0 and param.name == 'self'
        if param.is_self:
            self.self_param_name = param.name
            if param.lazy:
                raise YaqlException("Self parameter cannot be lazy")

    def get_num_params(self):
        if self._arg_spec.varargs or self._arg_spec.keywords:
            return -1
        if self.is_context_aware:
            return len(self._arg_spec.args) - 1
        else:
            return len(self._arg_spec.args)

    def get_context_owner_index(self):
        for param in self.param_definitions.values():
            if param.inverse_context:
                return param.name
        return None

    def build(self):
        for arg_name in self._arg_spec.args:
            if arg_name not in self.param_definitions:
                self.register_param_constraint(ParameterDefinition(arg_name))
        if self._arg_spec.varargs and\
                self._arg_spec.varargs not in self.param_definitions:
            self.register_param_constraint(
                ParameterDefinition(self._arg_spec.varargs))

    def inverse_context(self):
        self._inverse_context = True

    def __repr__(self):
        return self.function.func_name + "_" + str(self.get_num_params())

    def __call__(self, context, sender, *args):
        if sender and not self.self_param_name:
            raise YaqlExecutionException(
                "The function cannot be run as a method")

        num_args = len(args) + 1 if sender else len(args)

        if 0 <= self.get_num_params() != num_args:
            raise YaqlExecutionException(
                "Expected {0} args, got {1}".format(self.get_num_params(),
                                                    len(args)))

        input_position = 0
        prepared_list = []
        if self._inverse_context:
            context_to_pass = context
        else:
            context_to_pass = yaql.language.context.Context(context)

        for arg_name in self._arg_spec.args:
            definition = self.param_definitions[arg_name]
            if sender and definition.is_self:
                definition.validate_value(sender)
                prepared_list.append(sender)
            elif definition.is_context:
                prepared_list.append(context)
            else:
                arg = args[input_position]
                input_position += 1
                value, base_context = definition.validate(
                    arg.create_callable(context_to_pass))
                prepared_list.append(value)
                if self._inverse_context:
                    context_to_pass = yaql.language.context.Context(
                        base_context)
                else:
                    context_to_pass = yaql.language.context.Context(
                        context)

        if self._arg_spec.varargs:
            while input_position < len(args):
                definition = self.param_definitions[self._arg_spec.varargs]
                arg = args[input_position]
                input_position += 1
                c = arg.create_callable(context_to_pass)
                val = definition.validate(c)[0]
                base_context = c.yaql_context
                prepared_list.append(val)
                if self._inverse_context:
                    context_to_pass = yaql.language.context.Context(
                        base_context)
                else:
                    context_to_pass = yaql.language.context.Context(context)

        if self._inverse_context:
            final_context = context_to_pass
        else:
            final_context = context

        return self.function(*prepared_list), final_context

    def restrict_to_class(self, class_type):
        if self.self_param_name:
            definition = self.param_definitions.get(self.self_param_name)
            if not definition.arg_type:
                definition.arg_type = class_type


class ParameterDefinition(object):
    def __init__(self,
                 name,
                 lazy=False,
                 arg_type=None,
                 custom_validator=None,
                 constant_only=False,
                 function_only=False,
                 is_context=False,
                 is_self=None):
        self.arg_type = arg_type
        self.name = name
        self.lazy = lazy
        self.arg_type = arg_type
        self.custom_validator = custom_validator
        self.constant_only = constant_only
        self.function_only = function_only
        self.is_context = is_context
        self.is_self = is_self

    def validate(self, value):
        if self.constant_only:
            if not isinstance(value,
                              yaql.language.expressions.Constant.Callable):
                raise YaqlExecutionException(
                    "Parameter {0} has to be a constant".format(self.name))
        if self.function_only:
            if not isinstance(value,
                              yaql.language.expressions.Function.Callable):
                raise YaqlExecutionException(
                    "Parameter {0} has to be a function".format(self.name))
        if not self.lazy:
            try:
                res = value()
            except Exception as e:
                raise YaqlExecutionException(
                    "Unable to evaluate parameter {0}".format(self.name),
                    sys.exc_info())
        else:
            res = value

        context = value.yaql_context
        self.validate_value(res)
        return res, context

    def validate_value(self, value):
        if self.arg_type:
            # we need a special handling for booleans, as
            # isinstance(boolean_value, integer_type)
            # will return true, which is not what we expect
            if type(value) is types.BooleanType:
                if self.arg_type is not types.BooleanType:
                    raise YaqlExecutionException(
                        "Type of the parameter is not boolean")
            elif not isinstance(value, self.arg_type):
                raise YaqlExecutionException(
                    "Type of the parameter is not {0}".format(
                        str(self.arg_type)))
        if self.custom_validator:
            if not self.custom_validator(value):
                raise YaqlExecutionException(
                    "Parameter didn't pass the custom validation")


def parameter(name,
              lazy=False,
              arg_type=None,
              custom_validator=None,
              constant_only=False,
              function_only=False,
              is_context=False,
              is_self=None):
    def get_wrapper(func):
        param = ParameterDefinition(name,
                                    lazy,
                                    arg_type,
                                    custom_validator,
                                    constant_only,
                                    function_only,
                                    is_context,
                                    is_self)
        yaql_function(func).register_param_constraint(param)
        return func

    return get_wrapper


def inverse_context(func):
    yaql_function(func).inverse_context()
    return func


def context_aware(arg):
    if callable(arg):  # no-arg decorator case, arg is a decorated function
        yaql_function(arg).register_param_constraint(
            ParameterDefinition('context', is_context=True))
        return arg
    else:   # decorator is called with args, arg is the name of parameter
        return parameter(arg, is_context=True)
