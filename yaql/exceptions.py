class YaqlException(Exception):
    def __init__(self, message):
        super(YaqlException, self).__init__(message)


class NoFunctionRegisteredException(YaqlException):
    def __init__(self, func_name, arg_num=None):
        self.func_name = func_name
        self.arg_num = arg_num
        msg = "No function called '{0}' is registered".format(self.func_name)
        if self.arg_num:
            msg += " which has {0} arguments".format(self.arg_num)
        super(NoFunctionRegisteredException, self).__init__(msg)


class YaqlExecutionException(YaqlException):
    pass


class NoArgumentFound(YaqlException):
    def __init__(self, function_name, argument_name):
        message = \
            "Function '{0}' has no argument called '{1}'". \
            format(function_name, argument_name)
        super(NoArgumentFound, self).__init__(message)


class YaqlParsingException(YaqlException):
    def __init__(self, value, position):
        self.value = value
        self.position = position
        message = "Parse error: unexpected '{0}' at position {1}"\
            .format(self.value, self.position)
        super(YaqlParsingException, self).__init__(message)
