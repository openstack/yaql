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

import abc
import collections
import datetime

from dateutil import tz
import six

from yaql.language import exceptions
from yaql.language import expressions
from yaql.language import utils
from yaql import yaql_interface


@six.add_metaclass(abc.ABCMeta)
class HiddenParameterType(object):
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def check(self, value, context, engine, *args, **kwargs):
        return True


@six.add_metaclass(abc.ABCMeta)
class LazyParameterType(object):
    pass


@six.add_metaclass(abc.ABCMeta)
class SmartType(object):
    __slots__ = ('nullable',)

    def __init__(self, nullable):
        self.nullable = nullable

    def check(self, value, context, engine, *args, **kwargs):
        if value is None and not self.nullable:
            return False
        return True

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        if not self.check(value, context, engine, *args, **kwargs):
            raise exceptions.ArgumentValueException()
        utils.limit_memory_usage(engine, (1, value))
        return value

    def is_specialization_of(self, other):
        return False


class GenericType(SmartType):
    __slots__ = ('checker', 'converter')

    def __init__(self, nullable, checker=None, converter=None):
        super(GenericType, self).__init__(nullable)
        self.checker = checker
        self.converter = converter

    def check(self, value, context, engine, *args, **kwargs):
        if isinstance(value, expressions.Constant):
            value = value.value

        if not super(GenericType, self).check(
                value, context, engine, *args, **kwargs):
            return False
        if value is None or isinstance(value, expressions.Expression):
            return True
        if not self.checker:
            return True
        return self.checker(value, context, *args, **kwargs)

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        if isinstance(value, expressions.Constant):
            value = value.value
        super(GenericType, self).convert(
            value, receiver, context, function_spec, engine, *args, **kwargs)
        if value is None or not self.converter:
            return value
        return self.converter(value, receiver, context, function_spec, engine,
                              *args, **kwargs)


class PythonType(GenericType):
    __slots__ = ('python_type', 'validators')

    def __init__(self, python_type, nullable=True, validators=None):
        self.python_type = python_type
        if not validators:
            validators = [lambda _: True]
        if not isinstance(validators, (list, tuple)):
            validators = [validators]
        self.validators = validators

        super(PythonType, self).__init__(
            nullable,
            lambda value, context, *args, **kwargs: isinstance(
                value, self.python_type) and all(
                map(lambda t: t(value), self.validators)))

    def is_specialization_of(self, other):
        if not isinstance(other, PythonType):
            return False
        try:
            len(self.python_type)
            len(other.python_type)
        except Exception:
            return (
                issubclass(self.python_type, other.python_type)
                and not issubclass(other.python_type, self.python_type)
            )
        else:
            return False


class MappingRule(LazyParameterType, SmartType):
    __slots__ = tuple()

    def __init__(self):
        super(MappingRule, self).__init__(False)

    def check(self, value, context, *args, **kwargs):
        return isinstance(value, expressions.MappingRuleExpression)

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        super(MappingRule, self).convert(
            value, receiver, context, function_spec, engine, *args, **kwargs)
        wrap = lambda func: lambda: func(receiver, context, engine)

        return utils.MappingRule(wrap(value.source), wrap(value.destination))


class String(PythonType):
    __slots__ = tuple()

    def __init__(self, nullable=False):
        super(String, self).__init__(six.string_types, nullable=nullable)

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        value = super(String, self).convert(
            value, receiver, context, function_spec, engine, *args, **kwargs)
        return None if value is None else six.text_type(value)


class Integer(PythonType):
    __slots__ = tuple()

    def __init__(self, nullable=False):
        super(Integer, self).__init__(
            six.integer_types, nullable=nullable,
            validators=[lambda t: not isinstance(t, bool)])


class DateTime(PythonType):
    __slots__ = tuple()

    utctz = tz.tzutc()

    def __init__(self, nullable=False):
        super(DateTime, self).__init__(datetime.datetime, nullable=nullable)

    def convert(self, value, *args, **kwargs):
        if isinstance(value, datetime.datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=self.utctz)
            else:
                return value
        return super(DateTime, self).convert(value, *args, **kwargs)


class Iterable(PythonType):
    __slots__ = tuple()

    def __init__(self, validators=None, nullable=False):
        super(Iterable, self).__init__(
            collections.Iterable, nullable, [
                lambda t: not isinstance(t, six.string_types + (
                    utils.MappingType,))] + (validators or []))

    def check(self, value, context, engine, *args, **kwargs):
        if isinstance(value, utils.MappingType) and engine.options.get(
                'yaql.iterableDicts', False):
            return True
        return super(Iterable, self).check(
            value, context, engine, *args, **kwargs)

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        res = super(Iterable, self).convert(
            value, receiver, context, function_spec, engine, *args, **kwargs)
        return None if res is None else utils.limit_iterable(res, engine)


class Iterator(Iterable):
    __slots__ = tuple()

    def __init__(self, validators=None, nullable=False):
        super(Iterator, self).__init__(
            validators=[utils.is_iterator] + (validators or []),
            nullable=nullable)


class Sequence(PythonType):
    __slots__ = tuple()

    def __init__(self, validators=None, nullable=False):
        super(Sequence, self).__init__(
            collections.Sequence, nullable, [
                lambda t: not isinstance(t, six.string_types + (dict,))] + (
                    validators or []))


class Number(PythonType):
    __slots__ = tuple()

    def __init__(self, nullable=False):
        super(Number, self).__init__(
            six.integer_types + (float,), nullable,
            validators=[lambda t: not isinstance(t, bool)])


class Lambda(LazyParameterType, SmartType):
    __slots__ = tuple()

    def __init__(self, with_context=False, method=False):
        super(Lambda, self).__init__(True)
        self.with_context = with_context
        self.method = method

    def check(self, value, context, *args, **kwargs):
        if self.method and isinstance(
                value, expressions.Expression) and not value.uses_receiver:
            return False
        return super(Lambda, self).check(value, context, *args, **kwargs)

    @staticmethod
    def _publish_params(context, args, kwargs):
        for i, param in enumerate(args):
            context['$' + str(i + 1)] = param
        for arg_name, arg_value in kwargs.items():
            context['$' + arg_name] = arg_value

    def _call(self, value, receiver, context, engine, args, kwargs):
        self._publish_params(context, args, kwargs)
        if isinstance(value, expressions.Expression):
            result = value(receiver, context, engine)
        elif six.callable(value):
            result = value(*args, **kwargs)
        else:
            result = value
        return result

    def convert(self, value, receiver, context, function_spec, engine,
                *convert_args, **convert_kwargs):
        super(Lambda, self).convert(
            value, receiver, context, function_spec, engine,
            *convert_args, **convert_kwargs)
        if value is None:
            return None
        elif six.callable(value) and hasattr(value, '__unwrapped__'):
            value = value.__unwrapped__

        def func(*args, **kwargs):
            if self.method and self.with_context:
                new_receiver, new_context = args[:2]
                args = args[2:]
            elif self.method and not self.with_context:
                new_receiver, new_context = \
                    args[0], context.create_child_context()
                args = args[1:]
            elif not self.method and self.with_context:
                new_receiver, new_context = utils.NO_VALUE, args[0]
                args = args[1:]
            else:
                new_receiver, new_context = \
                    utils.NO_VALUE, context.create_child_context()

            return self._call(value, new_receiver, new_context,
                              engine, args, kwargs)

        func.__unwrapped__ = value
        return func


class Super(HiddenParameterType, SmartType):
    __slots__ = ('with_context', 'method', 'with_name')

    def __init__(self, with_context=False, method=None, with_name=False):
        self.with_context = with_context
        self.method = method
        self.with_name = with_name
        super(Super, self).__init__(False)

    @staticmethod
    def _find_function_context(spec, context):
        while context is not None:
            if spec in context:
                return context
            context = context.parent
        raise exceptions.NoFunctionRegisteredException(
            spec.name)

    def convert(self, value, receiver, context, function_spec, engine,
                *convert_args, **convert_kwargs):
        if six.callable(value) and hasattr(value, '__unwrapped__'):
            value = value.__unwrapped__

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

            new_receiver = receiver
            if self.method is True:
                new_receiver = args[0]
                args = args[1:]
            elif self.method is False:
                new_receiver = utils.NO_VALUE

            if self.with_context:
                new_context = args[0]
                args = args[1:]
            else:
                new_context = context.create_child_context()

            return parent_function_context(
                new_name, engine, new_receiver, new_context)(*args, **kwargs)
        func.__unwrapped__ = value
        return func


class Context(HiddenParameterType, SmartType):
    __slots__ = tuple()

    def __init__(self):
        super(Context, self).__init__(False)

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        return context


class Delegate(HiddenParameterType, SmartType):
    __slots__ = ('name', 'with_context', 'method', 'use_convention')

    def __init__(self, name=None, with_context=False, method=False,
                 use_convention=True):
        super(Delegate, self).__init__(False)
        self.name = name
        self.with_context = with_context
        self.method = method
        self.use_convention = use_convention

    def convert(self, value, receiver, context, function_spec, engine,
                *convert_args, **convert_kwargs):
        if six.callable(value) and hasattr(value, '__unwrapped__'):
            value = value.__unwrapped__

        def func(*args, **kwargs):
            name = self.name
            if not name:
                name = args[0]
                args = args[1:]

            new_receiver = utils.NO_VALUE
            if self.method:
                new_receiver = args[0]
                args = args[1:]
            if self.with_context:
                new_context = args[0]
                args = args[1:]
            else:
                new_context = context.create_child_context()

            return new_context(
                name, engine, new_receiver,
                use_convention=self.use_convention)(*args, **kwargs)
        func.__unwrapped__ = value
        return func


class Receiver(HiddenParameterType, SmartType):
    __slots__ = tuple()

    def __init__(self):
        super(Receiver, self).__init__(False)

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        return receiver


class Engine(HiddenParameterType, SmartType):
    __slots__ = tuple()

    def __init__(self):
        super(Engine, self).__init__(False)

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        return engine


class FunctionDefinition(HiddenParameterType, SmartType):
    __slots__ = tuple()

    def __init__(self):
        super(FunctionDefinition, self).__init__(False)

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        return function_spec


class Constant(SmartType):
    __slots__ = ('expand',)

    def __init__(self, nullable, expand=True):
        self.expand = expand
        super(Constant, self).__init__(nullable)

    def check(self, value, context, *args, **kwargs):
        return super(Constant, self).check(
            value, context, *args, **kwargs) and (
            value is None or isinstance(value, expressions.Constant))

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        super(Constant, self).convert(
            value, receiver, context, function_spec, engine, *args, **kwargs)
        return value.value if self.expand else value


class YaqlExpression(LazyParameterType, SmartType):
    __slots__ = ('_expression_type',)

    def __init__(self, expression_type=None):
        super(YaqlExpression, self).__init__(False)
        if expression_type and not utils.is_sequence(expression_type):
            expression_type = (expression_type,)
        self._expression_types = expression_type

    def check(self, value, context, *args, **kwargs):
        if not self._expression_types:
            return isinstance(value, expressions.Expression)
        return any(t == type(value) for t in self._expression_types)

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        super(YaqlExpression, self).convert(
            value, receiver, context, function_spec, engine, *args, **kwargs)
        return value


class StringConstant(Constant):
    __slots__ = tuple()

    def __init__(self, nullable=False):
        super(StringConstant, self).__init__(nullable)

    def check(self, value, context, *args, **kwargs):
        return super(StringConstant, self).check(
            value, context, *args, **kwargs) and (
            value is None or isinstance(value.value, six.string_types))


class Keyword(Constant):
    __slots__ = tuple()

    def __init__(self, expand=True):
        super(Keyword, self).__init__(False, expand)

    def check(self, value, context, *args, **kwargs):
        return isinstance(value, expressions.KeywordConstant)


class BooleanConstant(Constant):
    __slots__ = tuple()

    def __init__(self, nullable=False, expand=True):
        super(BooleanConstant, self).__init__(nullable, expand)

    def check(self, value, context, *args, **kwargs):
        return super(BooleanConstant, self).check(
            value, context, *args, **kwargs) and (
            value is None or type(value.value) is bool)


class NumericConstant(Constant):
    __slots__ = tuple()

    def __init__(self, nullable=False, expand=True):
        super(NumericConstant, self).__init__(nullable, expand)

    def check(self, value, context, *args, **kwargs):
        return super(NumericConstant, self).check(
            value, context, *args, **kwargs) and (
            value is None or isinstance(
                value.value, six.integer_types + (float,)) and
            type(value.value) is not bool)


@six.add_metaclass(abc.ABCMeta)
class SmartTypeAggregation(SmartType):
    __slots__ = ('types',)

    def __init__(self, *args, **kwargs):
        self.nullable = kwargs.pop('nullable', False)
        super(SmartTypeAggregation, self).__init__(self.nullable)

        self.types = []
        for item in args:
            if isinstance(item, (type, tuple)):
                item = PythonType(item)
            if isinstance(item, (HiddenParameterType, LazyParameterType)):
                raise ValueError('Special smart types are not supported')
            self.types.append(item)


class AnyOf(SmartTypeAggregation):
    __slots__ = tuple()

    def _check_match(self, value, context, engine, *args, **kwargs):
        for type_to_check in self.types:
            check_result = type_to_check.check(
                value, context, engine, *args, **kwargs)
            if check_result:
                return type_to_check

    def check(self, value, context, engine, *args, **kwargs):
        if isinstance(value, expressions.Constant):
            value = value.value

        if value is None:
            return self.nullable

        check_result = self._check_match(
            value, context, engine, *args, **kwargs)
        return True if check_result else False

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        if isinstance(value, expressions.Constant):
            value = value.value

        if value is None:
            if self.nullable:
                return None
            else:
                suitable_type = None
        else:
            suitable_type = self._check_match(
                value, context, engine, *args, **kwargs)
        if suitable_type:
            return suitable_type.convert(
                value, receiver, context, function_spec,
                engine, *args, **kwargs)
        raise exceptions.ArgumentValueException()


class Chain(SmartTypeAggregation):
    __slots__ = tuple()

    def _check_match(self, value, context, engine, *args, **kwargs):
        for type_to_check in self.types:
            check_result = type_to_check.check(
                value, context, engine, *args, **kwargs)
            if check_result:
                return type_to_check

    def check(self, value, context, engine, *args, **kwargs):
        if isinstance(value, expressions.Constant):
            value = value.value

        if value is None:
            return self.nullable

        for type_to_check in self.types:
            if not type_to_check.check(
                    value, context, engine, *args, **kwargs):
                return False

        return True

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        if isinstance(value, expressions.Constant):
            value = value.value

        if value is None:
            if self.nullable:
                return None
            raise exceptions.ArgumentValueException()

        for smart_type in self.types:
            value = smart_type.convert(
                value, receiver, context, function_spec,
                engine, *args, **kwargs)
        return value


class NotOfType(SmartType):
    __slots__ = ('smart_type',)

    def __init__(self, smart_type, nullable=True):
        if isinstance(smart_type, (type, tuple)):
            smart_type = PythonType(smart_type, nullable=nullable)
        self.smart_type = smart_type
        super(NotOfType, self).__init__(nullable)

    def check(self, value, context, engine, *args, **kwargs):
        if isinstance(value, expressions.Constant):
            value = value.value
        if not super(NotOfType, self).check(
                value, context, engine, *args, **kwargs):
            return False
        if value is None or isinstance(value, expressions.Expression):
            return True
        return not self.smart_type.check(
            value, context, engine, *args, **kwargs)


class YaqlInterface(HiddenParameterType, SmartType):
    __slots__ = tuple()

    def __init__(self):
        super(YaqlInterface, self).__init__(False)

    def convert(self, value, receiver, context, function_spec, engine,
                *args, **kwargs):
        return yaql_interface.YaqlInterface(context, engine, receiver)
