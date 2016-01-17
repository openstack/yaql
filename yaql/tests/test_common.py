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


class TestCommon(yaql.tests.TestCase):
    def test_null(self):
        self.assertIsNone(self.eval('null'))

    def test_true(self):
        res = self.eval('true')
        self.assertTrue(res)
        self.assertIsInstance(res, bool)

    def test_false(self):
        res = self.eval('false')
        self.assertFalse(res)
        self.assertIsInstance(res, bool)

    def test_string(self):
        self.assertEqual('True', self.eval('True'))
        self.assertEqual('some string', self.eval("'some string'"))

    def test_null_to_null(self):
        self.assertTrue(self.eval('null = null'))
        self.assertFalse(self.eval('null != null'))
        self.assertTrue(self.eval('null <= null'))
        self.assertTrue(self.eval('null >= null'))
        self.assertFalse(self.eval('null < null'))
        self.assertFalse(self.eval('null > null'))

    def test_ordering(self):
        self.assertTrue(self.eval('null < 0'))
        self.assertTrue(self.eval('null < true'))
        self.assertTrue(self.eval('null < false'))
        self.assertTrue(self.eval('null < a'))
        self.assertTrue(self.eval('null <= 0'))
        self.assertFalse(self.eval('null > 0'))
        self.assertFalse(self.eval('null >= 0'))
        self.assertTrue(self.eval('null != 0'))
        self.assertTrue(self.eval('null != false'))
        self.assertFalse(self.eval('null = false'))
        self.assertFalse(self.eval('null = 0'))
        self.assertFalse(self.eval('0 < null'))
        self.assertFalse(self.eval('0 <= null'))
        self.assertTrue(self.eval('0 >= null'))
        self.assertTrue(self.eval('0 > null'))

    def test_max(self):
        self.assertEqual(5, self.eval('max(1, 5)'))
        self.assertEqual(-1, self.eval('max(null, -1)'))
        self.assertIsNone(self.eval('max(null, null)'))

    def test_min(self):
        self.assertEqual(1, self.eval('min(1, 5)'))
        self.assertIsNone(self.eval('min(null, -1)'))
        self.assertIsNone(self.eval('min(null, null)'))

    def test_comparision_of_incomparable(self):
        self.assertFalse(self.eval('a = 1'))
        self.assertFalse(self.eval('a = false'))
        self.assertFalse(self.eval('a = null'))
        self.assertFalse(self.eval('[a] = [false]'))
        self.assertTrue(self.eval('a != 1'))
        self.assertTrue(self.eval('a != false'))
        self.assertTrue(self.eval('[a] != [false]'))
        self.assertTrue(self.eval('a != null'))
