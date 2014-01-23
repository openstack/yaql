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

if __name__ == '__main__':
    unittest.main()
