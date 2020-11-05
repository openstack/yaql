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
import re

import six


@six.add_metaclass(abc.ABCMeta)
class Convention(object):
    @abc.abstractmethod
    def convert_function_name(self, name):
        """
        Convert a function name into the given name.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        pass

    @abc.abstractmethod
    def convert_parameter_name(self, name):
        """
        Convert a parameter name to its name.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        pass


class PythonConvention(Convention):
    def convert_function_name(self, name):
        """
        Convert a function name into the name.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        return name

    def convert_parameter_name(self, name):
        """
        Convert a parameter name into a parameter name.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        return name


class CamelCaseConvention(Convention):
    def __init__(self):
        """
        Initialize the regex

        Args:
            self: (todo): write your description
        """
        self.regex = re.compile(r'(?!^)_(\w)', flags=re.UNICODE)

    def convert_function_name(self, name):
        """
        Converts a case name.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        return self._to_camel_case(name)

    def convert_parameter_name(self, name):
        """
        Converts a case name.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        return self._to_camel_case(name)

    def _to_camel_case(self, name):
        """
        Convert a camelcase to camelcase.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        return self.regex.sub(lambda m: m.group(1).upper(), name)
