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

import unittest
from yaql.tests import YaqlTest


class TestSystemFunctions(YaqlTest):
    def test_string_constant(self):
        self.assertEquals("abc", self.eval("abc"))
        self.assertEquals("100", self.eval("'100'"))
        self.assertEquals('some mw const', self.eval("'some mw const'"))

    def test_numeric_constant(self):
        self.assertEquals(0, self.eval('0'))
        self.assertEquals(100, self.eval('100'))
        self.assertEquals(0, self.eval("0"))
        self.assertEquals(100, self.eval("100"))

    def test_negative_constant(self):
        self.assertEquals(-10, self.eval('-10'))

    def test_int_arithmetic(self):
        self.assertEquals(20, self.eval('15+5'))
        self.assertEquals(20, self.eval('15+10-5'))
        self.assertEquals(20, self.eval('15+10-5*2+10/2'))
        self.assertEquals(2, self.eval('5/2'))
        self.assertEquals(3, self.eval('6/2'))

    def test_float_arithmetic(self):
        self.assertEquals(10.0, self.eval('5.0 * 2'))
        self.assertEquals(10.0, self.eval('5 * 2.0'))
        self.assertEquals(2.5, self.eval('5/2.0'))
        self.assertEquals(2.5, self.eval('5.0/2'))

    def test_mix_binary_unary(self):
        self.assertEquals(15, self.eval('20 + -5'))
        self.assertEquals(-25, self.eval('-20 + -5'))
        self.assertEquals(-25, self.eval('-20 - +5'))


if __name__ == '__main__':
    unittest.main()
