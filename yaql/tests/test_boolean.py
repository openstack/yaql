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

import yaql.tests


class TestBoolean(yaql.tests.TestCase):
    def test_and(self):
        self.assertTrue(self.eval('true and true'))
        self.assertFalse(self.eval('true and false'))
        self.assertFalse(self.eval('false and false'))
        self.assertFalse(self.eval('false and true'))
        self.assertEqual(12, self.eval('true and 12'))
        self.assertFalse(self.eval('null and null'))

    def test_or(self):
        self.assertTrue(self.eval('true or true'))
        self.assertTrue(self.eval('true or false'))
        self.assertFalse(self.eval('false or false'))
        self.assertTrue(self.eval('false or true'))
        self.assertEqual(12, self.eval('12 or true'))
        self.assertFalse(self.eval('null or null'))

    def test_not(self):
        self.assertFalse(self.eval('not true'))
        self.assertTrue(self.eval('not false'))
        self.assertTrue(self.eval('not 0'))
        self.assertFalse(self.eval('not 123'))
        self.assertTrue(self.eval("not ''"))
        self.assertFalse(self.eval("not True"))
        self.assertTrue(self.eval('not null'))

    def test_lazy(self):
        self.assertEqual(1, self.eval('$ or 10/($-1)', data=1))
        self.assertEqual(0, self.eval('$ and 10/$', data=0))

    def test_boolean_equality(self):
        self.assertTrue(self.eval('false = false'))
        self.assertTrue(self.eval('false != true'))
        self.assertTrue(self.eval('true != false'))
        self.assertTrue(self.eval('true = true'))
        self.assertFalse(self.eval('true = false'))
        self.assertFalse(self.eval('false = true'))
        self.assertFalse(self.eval('false != false'))
        self.assertFalse(self.eval('true != true'))

    def test_is_boolean(self):
        self.assertTrue(self.eval('isBoolean(true)'))
        self.assertTrue(self.eval('isBoolean(false)'))
        self.assertFalse(self.eval('isBoolean(123)'))
        self.assertFalse(self.eval('isBoolean(abc)'))
