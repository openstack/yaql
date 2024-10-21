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


class YaqlException(Exception):
    pass


class ResolutionError(YaqlException):
    pass


class FunctionResolutionError(ResolutionError):
    pass


class MethodResolutionError(ResolutionError):
    pass


class NoFunctionRegisteredException(FunctionResolutionError):
    def __init__(self, name):
        super().__init__(
            'Unknown function "{}"'.format(name))


class NoMethodRegisteredException(MethodResolutionError):
    def __init__(self, name, receiver):
        super().__init__(
            'Unknown method "{}" for receiver {}'.format(name, receiver))


class NoMatchingFunctionException(FunctionResolutionError):
    def __init__(self, name):
        super().__init__(
            'No function "{}" matches supplied arguments'.format(name))


class NoMatchingMethodException(MethodResolutionError):
    def __init__(self, name, receiver):
        super().__init__(
            'No method "{}" for receiver {} matches '
            'supplied arguments'.format(name, receiver))


class AmbiguousFunctionException(FunctionResolutionError):
    def __init__(self, name):
        super().__init__(
            'Ambiguous function "{}"'.format(name))


class AmbiguousMethodException(MethodResolutionError):
    def __init__(self, name, receiver):
        super().__init__(
            'Ambiguous method "{}" for receiver {}'.format(name, receiver))


class ArgumentException(YaqlException):
    def __init__(self, argument_name):
        self.parameter_name = argument_name
        super().__init__(
            'Invalid argument {}'.format(argument_name))


class MappingTranslationException(YaqlException):
    def __init__(self):
        super().__init__(
            'Cannot convert mapping to keyword argument')


class ArgumentValueException(YaqlException):
    def __init__(self):
        super().__init__()


class DuplicateParameterDecoratorException(YaqlException):
    def __init__(self, function_name, param_name):
        message = "Function '{0}' has multiple " \
                  "decorators for parameter '{1}'". \
            format(function_name, param_name)
        super().__init__(message)


class InvalidMethodException(YaqlException):
    def __init__(self, function_name):
        message = "Function '{0}' cannot be called as a method". \
            format(function_name)
        super().__init__(message)


class NoParameterFoundException(YaqlException):
    def __init__(self, function_name, param_name):
        message = "Function '{0}' has no parameter called '{1}'". \
            format(function_name, param_name)
        super().__init__(message)


class YaqlParsingException(YaqlException):
    def __init__(self, value, position, message):
        self.value = value
        self.position = position
        self.message = message
        super().__init__(message)


class YaqlGrammarException(YaqlParsingException):
    def __init__(self, expr, value, position):
        if position is None:
            msg = 'Parse error: unexpected end of statement'
        else:
            msg = "Parse error: unexpected '{}' at position {} of " \
                  "expression '{}'".format(value, position, expr)
        super().__init__(value, position, msg)


class YaqlLexicalException(YaqlParsingException):
    def __init__(self, value, position):
        msg = "Lexical error: illegal character '{}' at position {}" \
            .format(value, position)
        super().__init__(value, position, msg)


class InvalidOperatorTableException(YaqlException):
    def __init__(self, op):
        super(). \
            __init__("Invalid records in operator table for operator "
                     "'{}".format(op))


class WrappedException(YaqlException):
    def __init__(self, exception):
        self.wrapped = exception
        super().__init__(str(exception))


class CollectionTooLargeException(YaqlException):
    def __init__(self, count):
        super().__init__(
            'Collection length exceeds {} elements'.format(count))


class MemoryQuotaExceededException(YaqlException):
    def __init__(self):
        super().__init__(
            'Expression consumed too much memory')
