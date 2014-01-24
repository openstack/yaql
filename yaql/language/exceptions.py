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


class YaqlException(Exception):
    def __init__(self, message):
        super(YaqlException, self).__init__()
        self.message = message


class NoFunctionRegisteredException(YaqlException):
    def __init__(self, func_name, arg_num=None):
        self.func_name = func_name
        self.arg_num = arg_num
        msg = "No function called '{0}' is registered".format(self.func_name)
        if self.arg_num:
            msg += " which has {0} arguments".format(self.arg_num)
        super(NoFunctionRegisteredException, self).__init__(msg)


class YaqlExecutionException(YaqlException):
    def __init__(self, message, inner=None):
        super(YaqlExecutionException, self).__init__(message)
        self.inner_exception = inner


class DuplicateParameterDecoratorException(YaqlException):
    def __init__(self, function_name, param_name):
        message = "Function '{0}' has multiple " \
                  "decorators for parameter '{1}'". \
            format(function_name, param_name)
        super(DuplicateParameterDecoratorException, self).__init__(message)


class DuplicateContextDecoratorException(YaqlException):
    def __init__(self, function_name):
        message = "Function '{0}' has multiple context-param decorators". \
            format(function_name)
        super(DuplicateContextDecoratorException, self).__init__(message)


class DuplicateContextOwnerDecoratorException(YaqlException):
    def __init__(self, function_name):
        message = "Function '{0}' has multiple context-owner decorators". \
            format(function_name)
        super(DuplicateContextOwnerDecoratorException, self).__init__(message)


class NoParameterFoundException(YaqlException):
    def __init__(self, function_name, param_name):
        message = "Function '{0}' has no parameter called '{1}'". \
            format(function_name, param_name)
        super(NoParameterFoundException, self).__init__(message)


class YaqlParsingException(YaqlException):
    def __init__(self, value, position, message):
        self.value = value
        self.position = position
        self.message = message
        super(YaqlParsingException, self).__init__(message)


class YaqlGrammarException(YaqlParsingException):
    def __init__(self, value, position):
        msg = "Parse error: unexpected '{0}' at position {1}" \
            .format(value, position)
        super(YaqlGrammarException, self).__init__(value, position, msg)


class YaqlLexicalException(YaqlParsingException):
    def __init__(self, value, position):
        msg = "Lexical error: illegal character '{0}' at position {1}" \
            .format(value, position)
        super(YaqlLexicalException, self).__init__(value, position, msg)


class YaqlSequenceException(YaqlException):
    def __init__(self, size):
        self.size = size
        super(YaqlSequenceException, self). \
            __init__("Generator sequence too long ({0})".format(self.size))
