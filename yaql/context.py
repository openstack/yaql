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
from exceptions import NoArgumentFound


class Context(object):
    def __init__(self, parent_context=None, data=None):
        self.parent_context = parent_context
        self.functions = {}
        self.data = {}
        if data:
            self.data['$'] = data
        if parent_context:
            self.depth = parent_context.depth + 1
        else:
            self.depth = 0

    def register_function(self, function, name):
        if hasattr(function, "is_context_aware"):
            num_params = function.context_aware.get_num_callable_args()
            if function.context_aware.varargs:
                num_params = 0
        else:
            argspec = inspect.getargspec(function)
            num_params = len(argspec.args)
            if argspec.varargs:
                num_params = 0
        if not num_params:
            num_params = '*'
        if not name in self.functions:
            self.functions[name] = {}
        if not num_params in self.functions[name]:
            self.functions[name][num_params] = [function]
        else:
            self.functions[name][num_params].append(function)

    def get_functions(self, function_name, num_params):
        result = []
        if function_name in self.functions:
            if num_params in self.functions[function_name]:
                result += self.functions[function_name][num_params]
            if '*' in self.functions[function_name]:
                result += self.functions[function_name]['*']

        if self.parent_context:
            result += self.parent_context.get_functions(function_name,
                                                        num_params)
        return result

    def set_data(self, data, path='$'):
        if not path.startswith('$'):
            path = '$' + path
        self.data[path] = data
        if path == '$':
            self.data['$1'] = data

    def get_data(self, path='$', default=None):
        if not path.startswith('$'):
            path = '$' + path
        if path in self.data:
            return self.data[path]
        if self.parent_context:
            return self.parent_context.get_data(path, default)
        else:
            return default

    def __contains__(self, item):
        if not item.startswith('$'):
            item = '$' + item
        if item in self.data:
            return True
        elif self.parent_context:
            return item in self.parent_context
        else:
            return False


class EvalArg(object):
    def __init__(self, arg_name, arg_type=None, custom_validator=None):
        self.arg_name = arg_name
        self.arg_type = arg_type
        self.custom_validator = custom_validator

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
        return len(self.real_args)-1

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
        # if hasattr(function, 'arg_requirements'):
        #     f.arg_requirements = function.arg_requirements
        return f

