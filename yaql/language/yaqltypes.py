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

import collections

import six

from yaql.language import exceptions
from yaql.language import expressions
from yaql.language import utils


class HiddenParameterType(object):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def check(self, value):
        return True


class LazyParameterType(object):
    pass


class SmartType(object):
    def __init__(self, nullable):
        self.nullable = nullable

    def check(self, value):
        if value is None and not self.nullable:
            return False
        return True

    def convert(self, value, sender, context, function_spec, engine):
        if not self.check(value):
            raise exceptions.ArgumentValueException()
        utils.limit_memory_usage(engine, (1, value))

    def is_specialization_of(self, other):
        return False


class PythonType(SmartType):
    def __init__(self, python_type, nullable=True, validators=None):
        self.python_type = python_type
        if not validators:
            validators = [lambda _: True]
        if not isinstance(validators, (list, tuple)):
            validators = [validators]
        self.validators = validators
        super(PythonType, self).__init__(nullable)

    def check(self, value):
        if isinstance(value, expressions.Constant):
            value = value.value

        return super(PythonType, self).check(value) and (
            value is None or isinstance(value, expressions.Expression) or (
                isinstance(value, self.python_type) and all(
                    map(lambda t: t(value), self.validators))))

    def convert(self, value, sender, context, function_spec, engine):
        super(PythonType, self).convert(value, sender, context,
                                        function_spec, engine)
        if isinstance(value, expressions.Constant):
            value = value.value
        super(PythonType, self).convert(value, sender, context,
                                        function_spec, engine)
        return value

    def is_specialization_of(self, other):
        return (
            isinstance(other, PythonType)
            and issubclass(self.python_type, other.python_type)
            and not issubclass(other.python_type, self.python_type)
        )


class MappingRule(LazyParameterType, SmartType):
    def __init__(self):
        super(MappingRule, self).__init__(False)

    def check(self, value):
        return isinstance(value, expressions.MappingRuleExpression)

    def convert(self, value, sender, context, function_spec, engine):
        super(MappingRule, self).convert(value, sender, context,
                                         function_spec, engine)
        wrap = lambda func: lambda: func(sender, context, engine)[0]

        return utils.MappingRule(wrap(value.source), wrap(value.destination))


class String(PythonType):
    def __init__(self, nullable=False):
        super(String, self).__init__(six.string_types, nullable=nullable)

    def convert(self, value, sender, context, function_spec, engine):
        value = super(String, self).convert(value, sender, context,
                                            function_spec, engine)
        return None if value is None else six.text_type(value)


class Iterable(PythonType):
    def __init__(self, validators=None):
        super(Iterable, self).__init__(
            collections.Iterable, False, [
                lambda t: not isinstance(t, six.string_types + (
                    utils.MappingType,))] + (validators or []))

    def convert(self, value, sender, context, function_spec, engine):
        res = super(Iterable, self).convert(value, sender, context,
                                            function_spec, engine)
        return utils.limit_iterable(res, engine)


class Iterator(Iterable):
    def __init__(self, validators=None):
        super(Iterator, self).__init__(
            validators=[utils.is_iterator] + (validators or []))


class Sequence(PythonType):
    def __init__(self, validators=None):
        super(Sequence, self).__init__(
            collections.Sequence, False, [
                lambda t: not isinstance(t, six.string_types + (dict,))] + (
                    validators or []))


class Number(PythonType):
    def __init__(self, nullable=False):
        super(Number, self).__init__(
            six.integer_types + (float,), nullable, [
                lambda t: type(t) is not bool])


class Lambda(LazyParameterType, SmartType):
    def __init__(self, with_context=False, method=False, return_context=False):
        super(Lambda, self).__init__(True)
        self.return_context = return_context
        self.with_context = with_context
        self.method = method

    def check(self, value):
        if self.method and isinstance(
                value, expressions.Expression) and not value.uses_sender:
            return False
        return super(Lambda, self).check(value)

    @staticmethod
    def _publish_params(context, args, kwargs):
        for i, param in enumerate(args):
            context['$' + str(i + 1)] = param
        for arg_name, arg_value in kwargs.items():
            context['$' + arg_name] = arg_value

    def _call(self, value, sender, context, engine, args, kwargs):
        self._publish_params(context, args, kwargs)
        if isinstance(value, expressions.Expression):
            result = value(sender, context, engine)
        elif six.callable(value):
            result = value, context
        else:
            result = value, context
        return result[0] if not self.return_context else result

    def convert(self, value, sender, context, function_spec, engine):
        super(Lambda, self).convert(value, sender, context,
                                    function_spec, engine)
        if value is None:
            return None

        def func(*args, **kwargs):
            if self.method and self.with_context:
                new_sender, new_context = args[:2]
                args = args[2:]
            elif self.method and not self.with_context:
                new_sender, new_context = \
                    args[0], context.create_child_context()
                args = args[1:]
            elif not self.method and self.with_context:
                new_sender, new_context = utils.NO_VALUE, args[0]
                args = args[1:]
            else:
                new_sender, new_context = \
                    utils.NO_VALUE, context.create_child_context()

            return self._call(value, new_sender, new_context,
                              engine, args, kwargs)

        return func


class Super(HiddenParameterType, SmartType):
    def __init__(self, with_context=False, method=None, return_context=False,
                 with_name=False):
        self.return_context = return_context
        self.with_context = with_context
        self.method = method
        self.with_name = with_name
        super(Super, self).__init__(False)

    @staticmethod
    def _find_function_context(spec, context):
        while context is not None:
            funcs = context.get_functions(spec.name)
            if funcs and spec in funcs:
                return context
            context = context.parent
        raise exceptions.NoFunctionRegisteredException(
            spec.name)

    def convert(self, value, sender, context, function_spec, engine):
        def func(*args, **kwargs):
            function_context = self._find_function_context(
                function_spec, context)
            parent_function_context = function_context.parent
            if parent_function_context is None:
                raise exceptions.NoFunctionRegisteredException(
                    function_spec.name)

            new_name = function_spec.name
            if self.with_name:
                new_name = args[0]
                args = args[1:]

            new_sender = sender
            if self.method is True:
                new_sender = args[0]
                args = args[1:]
            elif self.method is False:
                new_sender = utils.NO_VALUE

            if self.with_context:
                new_context = args[0]
                args = args[1:]
            else:
                new_context = context.create_child_context()

            return parent_function_context(
                new_name, engine, new_sender, new_context,
                self.return_context)(*args, **kwargs)
        return func


class Context(HiddenParameterType, SmartType):
    def __init__(self):
        super(Context, self).__init__(False)

    def convert(self, value, sender, context, function_spec, engine):
        return context


class Delegate(HiddenParameterType, SmartType):
    def __init__(self, name=None, with_context=False, method=False,
                 return_context=False):
        super(Delegate, self).__init__(False)
        self.name = name
        self.return_context = return_context
        self.with_context = with_context
        self.method = method

    def convert(self, value, sender, context, function_spec, engine):
        def func(*args, **kwargs):
            name = self.name
            if not name:
                name = args[0]
                args = args[1:]

            new_sender = utils.NO_VALUE
            if self.method:
                new_sender = args[0]
                args = args[1:]
            if self.with_context:
                new_context = args[0]
                args = args[1:]
            else:
                new_context = context.create_child_context()

            return new_context(
                name, engine, new_sender, return_context=self.return_context,
                use_convention=True)(*args, **kwargs)
        return func


class Sender(HiddenParameterType, SmartType):
    def __init__(self):
        super(Sender, self).__init__(False)

    def convert(self, value, sender, context, function_spec, engine):
        return sender


class Engine(HiddenParameterType, SmartType):
    def __init__(self):
        super(Engine, self).__init__(False)

    def convert(self, value, sender, context, function_spec, engine):
        return engine


class FunctionDefinition(HiddenParameterType, SmartType):
    def __init__(self):
        super(FunctionDefinition, self).__init__(False)

    def convert(self, value, sender, context, function_spec, engine):
        return function_spec


class Constant(SmartType):
    def __init__(self, nullable, expand=True):
        self.expand = expand
        super(Constant, self).__init__(nullable)

    def check(self, value):
        return super(Constant, self).check(value.value) and (
            value is None or isinstance(value, expressions.Constant))

    def convert(self, value, sender, context, function_spec, engine):
        super(Constant, self).convert(value, sender, context,
                                      function_spec, engine)
        return value.value if self.expand else value


class YaqlExpression(LazyParameterType, SmartType):
    def __init__(self):
        super(YaqlExpression, self).__init__(False)

    def check(self, value):
        return isinstance(value, expressions.Expression)

    def convert(self, value, sender, context, function_spec, engine):
        super(YaqlExpression, self).convert(value, sender, context,
                                            function_spec, engine)
        return value


class StringConstant(Constant):
    def __init__(self, nullable=False):
        super(StringConstant, self).__init__(nullable)

    def check(self, value):
        return super(StringConstant, self).check(value) and (
            value is None or isinstance(value.value, six.string_types))


class Keyword(Constant):
    def __init__(self, expand=True):
        super(Keyword, self).__init__(False, expand)

    def check(self, value):
        return isinstance(value, expressions.KeywordConstant)


class BooleanConstant(Constant):
    def __init__(self, nullable=False, expand=True):
        super(BooleanConstant, self).__init__(nullable, expand)

    def check(self, value):
        return super(BooleanConstant, self).check(value) and (
            value is None or type(value.value) is bool)


class NumericConstant(Constant):
    def __init__(self, nullable=False, expand=True):
        super(NumericConstant, self).__init__(nullable, expand)

    def check(self, value):
        return super(NumericConstant, self).check(value) and (
            value is None or isinstance(
                value.value, six.integer_types + (float,)) and
            type(value.value) is not bool)
