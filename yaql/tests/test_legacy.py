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

from yaql.language import exceptions
import yaql.tests


class TestLegacyNewEngine(yaql.tests.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestLegacyNewEngine, self).__init__(*args, **kwargs)
        self.eval = self.legacy_eval_new_engine

    def test_dict(self):
        self.assertEqual(
            {'a': 'b', 1: 2, None: None},
            self.eval('dict(1 => 2, a => b, null => null)'))

        self.assertEqual({}, self.eval('dict()'))

    def test_list(self):
        self.assertEqual([1, 2, 'a', None], self.eval('list(1, 2, a, null)'))
        self.assertEqual([], self.eval('list()'))
        self.assertEqual([1, 2], self.eval('[1, 2].select($).list()'))

    def test_dict_get(self):
        self.assertEqual(5, self.eval("get($, 'a b')", data={'a b': 5}))
        self.assertEqual(5, self.eval("$.get('a b')", data={'a b': 5}))

    def test_int(self):
        self.assertEqual(5, self.eval("'5'.int()"))
        self.assertEqual(5, self.eval('5.2.int()'))
        self.assertEqual(0, self.eval('null.int()'))

    def test_float(self):
        self.assertAlmostEqual(5.1, self.eval("'5.1'.float()"))
        self.assertAlmostEqual(5.0, self.eval('5.float()'))
        self.assertAlmostEqual(5.1, self.eval("float('5.1')"))
        self.assertAlmostEqual(5.0, self.eval("float(5)"))
        self.assertEqual(0, self.eval('null.float()'))

    def test_bool(self):
        self.assertFalse(self.eval('null.bool()'))
        self.assertFalse(self.eval("''.bool()"))
        self.assertFalse(self.eval('0.bool()'))
        self.assertFalse(self.eval('false.bool()'))
        self.assertFalse(self.eval('[].bool()'))
        self.assertFalse(self.eval('{}.bool()'))
        self.assertTrue(self.eval("' '.bool()"))
        self.assertTrue(self.eval('x.bool()'))
        self.assertTrue(self.eval('1.bool()'))
        self.assertTrue(self.eval('true.bool()'))
        self.assertTrue(self.eval('[1].bool()'))
        self.assertTrue(self.eval('{a=>b}.bool()'))

    def test_filter(self):
        self.assertEqual(2, self.eval("list(1,2,3)[1]"))
        self.assertEqual(3, self.eval("list(1,2,3)[$]", data=2))
        self.assertEqual([1, 3], self.eval("list(1,2,3)[$ != 2]"))
        self.assertEqual([], self.eval("list()[$ > 0]"))

    def test_sum(self):
        self.assertEqual(6, self.eval('list(1,2,3).sum()'))
        self.assertEqual(6, self.eval('sum(list(1,2,3))'))

    def test_range(self):
        self.assertEqual([2, 3, 4, 5], self.eval('range(2).take(4)'))
        self.assertEqual([1, 2, 3], self.eval('range(1, 4)'))
        self.assertEqual([2, 3, 4, 5], self.eval('2.range().take(4)'))
        self.assertEqual([1, 2, 3], self.eval('1.range(4)'))

    def test_take_while(self):
        self.assertEqual([1, 2], self.eval('[1, 2, 3, 4].takeWhile($ < 3)'))
        self.assertEqual([1, 2], self.eval('takeWhile([1, 2, 3, 4], $ < 3)'))

    def test_switch(self):
        expr = 'switch($, $ > 10 => 1, $ <= 10 => -1)'
        self.assertEqual(1, self.eval(expr, data=15))
        self.assertEqual(-1, self.eval(expr, data=5))

    def test_as(self):
        self.assertEqual(
            [3, 6],
            self.eval('[1, 2].as(sum($) => a).select($ * $a)'))

    def test_distinct(self):
        data = [1, 2, 3, 2, 4, 8]
        self.assertEqual([1, 2, 3, 4, 8], self.eval('$.distinct()', data=data))
        self.assertEqual([1, 2, 3, 4, 8], self.eval('distinct($)', data=data))

        data = [{'a': 1}, {'b': 2}, {'a': 1}]
        self.assertEqual(
            [{'a': 1}, {'b': 2}],
            self.eval('$.distinct()', data=data))

    def test_keyword_dict_access(self):
        data = {'A': 12, 'b c': 44, '__d': 99, '_e': 999}
        self.assertEqual(12, self.eval('$.A', data=data))
        self.assertEqual(999, self.eval('$._e', data=data))

        self.assertRaises(exceptions.NoMatchingFunctionException,
                          self.eval, "$.'b c'", data=data)
        self.assertRaises(exceptions.NoMatchingFunctionException,
                          self.eval, '$.123', data=data)
        self.assertIsNone(self.eval('$.b', data=data))
        self.assertRaises(exceptions.YaqlLexicalException,
                          self.eval, '$.__d', data=data)

    def test_compare_not_comparable(self):
        self.assertTrue(self.eval('asd != true'))
        self.assertFalse(self.eval('asd = 0'))


class TestLegacy(TestLegacyNewEngine):
    def __init__(self, *args, **kwargs):
        super(TestLegacy, self).__init__(*args, **kwargs)
        self.eval = self.legacy_eval

    def test_tuples_func(self):
        self.assertEqual((1, 2), self.eval('tuple(1, 2)'))
        self.assertEqual((None,), self.eval('tuple(null)'))
        self.assertEqual((), self.eval('tuple()'))

    def test_tuples(self):
        self.assertEqual((1, 2), self.eval('1 => 2'))
        self.assertEqual((None, 'a b'), self.eval('null => "a b"'))
        self.assertEqual((1, 2, 3), self.eval('1 => 2 => 3'))
        self.assertEqual(((1, 2), 3), self.eval('(1 => 2) => 3'))
        self.assertEqual((1, (2, 3)), self.eval('1 => (2 => 3)'))

    def test_dicts_are_iterable(self):
        data = {'a': 1, 'b': 2}
        self.assertTrue(self.eval('a in $', data))
        self.assertItemsEqual('ab', self.eval('$.sum()', data))
