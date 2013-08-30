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

import inspect


class Context():
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


    def get_data(self, path='$'):
        if path in self.data:
            return self.data[path]
        if self.parent_context:
            return self.parent_context.get_data(path)