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
        """
        Initialize the given name.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        super(NoFunctionRegisteredException, self).__init__(
            u'Unknown function "{0}"'.format(name))


class NoMethodRegisteredException(MethodResolutionError):
    def __init__(self, name, receiver):
        """
        Initialize a receiver.

        Args:
            self: (todo): write your description
            name: (str): write your description
            receiver: (callable): write your description
        """
        super(NoMethodRegisteredException, self).__init__(
            u'Unknown method "{0}" for receiver {1}'.format(name, receiver))


class NoMatchingFunctionException(FunctionResolutionError):
    def __init__(self, name):
        """
        Initialize a new matching

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        super(NoMatchingFunctionException, self).__init__(
            u'No function "{0}" matches supplied arguments'.format(name))


class NoMatchingMethodException(MethodResolutionError):
    def __init__(self, name, receiver):
        """
        Initialize receiver

        Args:
            self: (todo): write your description
            name: (str): write your description
            receiver: (callable): write your description
        """
        super(NoMatchingMethodException, self).__init__(
            u'No method "{0}" for receiver {1} matches '
            u'supplied arguments'.format(name, receiver))


class AmbiguousFunctionException(FunctionResolutionError):
    def __init__(self, name):
        """
        Initialize the class.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        super(AmbiguousFunctionException, self).__init__(
            u'Ambiguous function "{0}"'.format(name))


class AmbiguousMethodException(MethodResolutionError):
    def __init__(self, name, receiver):
        """
        Initialize a receiver

        Args:
            self: (todo): write your description
            name: (str): write your description
            receiver: (callable): write your description
        """
        super(AmbiguousMethodException, self).__init__(
            u'Ambiguous method "{0}" for receiver {1}'.format(name, receiver))


class ArgumentException(YaqlException):
    def __init__(self, argument_name):
        """
        Initialize a new argument.

        Args:
            self: (todo): write your description
            argument_name: (str): write your description
        """
        self.parameter_name = argument_name
        super(ArgumentException, self).__init__(
            u'Invalid argument {0}'.format(argument_name))


class MappingTranslationException(YaqlException):
    def __init__(self):
        """
        Initialize the mapping

        Args:
            self: (todo): write your description
        """
        super(MappingTranslationException, self).__init__(
            u'Cannot convert mapping to keyword argument')


class ArgumentValueException(YaqlException):
    def __init__(self):
        """
        Initialize the class

        Args:
            self: (todo): write your description
        """
        super(ArgumentValueException, self).__init__()


class DuplicateParameterDecoratorException(YaqlException):
    def __init__(self, function_name, param_name):
        """
        Initialize a function.

        Args:
            self: (todo): write your description
            function_name: (str): write your description
            param_name: (str): write your description
        """
        message = u"Function '{0}' has multiple " \
                  u"decorators for parameter '{1}'". \
            format(function_name, param_name)
        super(DuplicateParameterDecoratorException, self).__init__(message)


class InvalidMethodException(YaqlException):
    def __init__(self, function_name):
        """
        Initialize a function.

        Args:
            self: (todo): write your description
            function_name: (str): write your description
        """
        message = u"Function '{0}' cannot be called as a method". \
            format(function_name)
        super(InvalidMethodException, self).__init__(message)


class NoParameterFoundException(YaqlException):
    def __init__(self, function_name, param_name):
        """
        Initialize a function.

        Args:
            self: (todo): write your description
            function_name: (str): write your description
            param_name: (str): write your description
        """
        message = u"Function '{0}' has no parameter called '{1}'". \
            format(function_name, param_name)
        super(NoParameterFoundException, self).__init__(message)


class YaqlParsingException(YaqlException):
    def __init__(self, value, position, message):
        """
        Initialize the message.

        Args:
            self: (todo): write your description
            value: (todo): write your description
            position: (int): write your description
            message: (str): write your description
        """
        self.value = value
        self.position = position
        self.message = message
        super(YaqlParsingException, self).__init__(message)


class YaqlGrammarException(YaqlParsingException):
    def __init__(self, expr, value, position):
        """
        Creates a new gram expression.

        Args:
            self: (todo): write your description
            expr: (todo): write your description
            value: (todo): write your description
            position: (int): write your description
        """
        if position is None:
            msg = u'Parse error: unexpected end of statement'
        else:
            msg = u"Parse error: unexpected '{0}' at position {1} of " \
                  u"expression '{2}'".format(value, position, expr)
        super(YaqlGrammarException, self).__init__(value, position, msg)


class YaqlLexicalException(YaqlParsingException):
    def __init__(self, value, position):
        """
        Initialize the underlying position.

        Args:
            self: (todo): write your description
            value: (todo): write your description
            position: (int): write your description
        """
        msg = u"Lexical error: illegal character '{0}' at position {1}" \
            .format(value, position)
        super(YaqlLexicalException, self).__init__(value, position, msg)


class InvalidOperatorTableException(YaqlException):
    def __init__(self, op):
        """
        Initialize the op.

        Args:
            self: (todo): write your description
            op: (todo): write your description
        """
        super(InvalidOperatorTableException, self). \
            __init__(u"Invalid records in operator table for operator "
                     u"'{0}".format(op))


class WrappedException(YaqlException):
    def __init__(self, exception):
        """
        Initialize the exception.

        Args:
            self: (todo): write your description
            exception: (todo): write your description
        """
        self.wrapped = exception
        super(WrappedException, self).__init__(str(exception))


class CollectionTooLargeException(YaqlException):
    def __init__(self, count):
        """
        Initialize a count.

        Args:
            self: (todo): write your description
            count: (int): write your description
        """
        super(CollectionTooLargeException, self).__init__(
            'Collection length exceeds {0} elements'.format(count))


class MemoryQuotaExceededException(YaqlException):
    def __init__(self):
        """
        Initialize the device memory.

        Args:
            self: (todo): write your description
        """
        super(MemoryQuotaExceededException, self).__init__(
            'Expression consumed too much memory')
