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


class TestConst(YaqlTest):
    def test_string_constant(self):
        self.assertEquals("abc", self.eval("abc"))
        self.assertEquals("100", self.eval("'100'"))
        self.assertEquals('some mw const', self.eval("'some mw const'"))
        self.assertEquals('i\'m fine', self.eval("'i\\'m fine'"))

    def test_numeric_constant(self):
        self.assertEquals(0, self.eval('0'))
        self.assertEquals(100, self.eval('100'))
        self.assertEquals(0, self.eval("0"))
        self.assertEquals(100, self.eval("100"))

    def test_negative_constant(self):
        self.assertEquals(-10, self.eval('-10'))

    def test_boolean_constant(self):
        self.assertEquals(True, self.eval('true'))
        self.assertEquals(False, self.eval('false'))
        self.assertNotEquals(True, self.eval('True'))
        self.assertNotEquals(False, self.eval('False'))

    def test_r_multiline(self):
        self.assertEval(10, '3 +\r 7')

    def test_n_multiline(self):
        self.assertEval(10, '3 +\n 7')

    def test_rn_multiline(self):
        self.assertEval(10, '3\r\n +\r\n 7')


if __name__ == '__main__':
    unittest.main()
