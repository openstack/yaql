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
from yaql.language.exceptions import YaqlExecutionException

from yaql.tests import YaqlTest


import unittest


class TestStrings(YaqlTest):
    def test_string_concat(self):
        expression = "abc + cdef + ' qw er'"
        self.assertEquals('abccdef qw er', self.eval(expression))

    def test_string_to_list(self):
        expression = "abc.asList()"
        expression2 = "abc.asList()[1]"
        self.assertEquals(['a', 'b', 'c'], self.eval(expression))
        self.assertEquals('b', self.eval(expression2))

    def test_string_conversion_function(self):
        self.assertEval("42", "string(42)")

    def test_string_conversion_method(self):
        self.assertEval("42", "42.to_string()")

    def test_string_conversion_method_as_function(self):
        self.assertEval("42", "to_string(42)")

    def test_unable_to_call_string_as_method(self):
        self.assertRaises(YaqlExecutionException, self.eval, "42.string")


if __name__ == '__main__':
    unittest.main()
