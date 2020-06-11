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


class TestCollections(yaql.tests.TestCase):
    def test_list(self):
        self.assertEqual([], self.eval('list()'))
        self.assertEqual([1, 2, 3], self.eval('list(1, 2, 3)'))
        self.assertEqual([1, 2, [3, 4]], self.eval('list(1, 2, list(3, 4))'))

    def test_list_expr(self):
        self.assertEqual([1, 2, 3], self.eval('[1,2,3]'))
        self.assertEqual([2, 4], self.eval('[1,[2]][1] + [3, [4]][1]'))
        self.assertEqual([1, 2, 3, 4], self.eval('[1,2] + [3, 4]'))
        self.assertEqual(2, self.eval('([1,2] + [3, 4])[1]'))
        self.assertEqual([], self.eval('[]'))

    def test_list_from_iterator(self):
        iterator = (i for i in range(3))
        self.assertEqual([0, 1, 2], self.eval('list($)', data=iterator))

    def test_to_list(self):
        data = (i for i in range(3))
        self.assertEqual([0, 1, 2], self.eval('$.toList()', data=data))

        data = [0, 1, 2]
        self.assertEqual([0, 1, 2], self.eval('$.toList()', data=data))

        data = (0, 1, 2)
        self.assertEqual([0, 1, 2], self.eval('$.toList()', data=data))

        data = {'a': 1, 'b': 2}

        self.assertTrue(self.eval('isList($.keys().toList())', data=data))

    def test_list_concatenates_and_flatten_generators(self):
        generator_func = lambda: (i for _ in range(2)   # noqa: E731
                                  for i in range(3))

        self.context['$seq1'] = generator_func()
        self.context['$seq2'] = generator_func()

        self.assertEqual([0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2],
                         self.eval('list($seq1, $seq2)'))

    def test_indexer_list_access(self):
        data = [1, 2, 3]
        self.assertEqual(1, self.eval('$[0]', data=data))
        self.assertEqual(3, self.eval('$[-1]', data=data))
        self.assertEqual(2, self.eval('$[-1-1]', data=data))
        self.assertRaises(IndexError,
                          self.eval, "$[3]", data=data)
        self.assertRaises(IndexError,
                          self.eval, "$[-4]", data=data)
        self.assertRaises(exceptions.NoMatchingFunctionException,
                          self.eval, "$[a]", data=data)

    def test_dict(self):
        self.assertEqual(
            {'b c': 13, 'a': 2, 4: 5, None: None, True: False, 8: 8},
            self.eval("dict(a => 2, 'b c' => 13, 4 => 5, "
                      "null => null, true => false, 2+6=>8)"))

    def test_dict_expr(self):
        self.assertEqual(
            {'b c': 13, 'a': 2, 4: 5, None: None, True: False, 8: 8},
            self.eval("{a => 2, 'b c' => 13, 4 => 5, "
                      "null => null, true => false, 2+6=>8}"))

        self.assertEqual({'b': 2, 'a': 1}, self.eval('{a => 1} + {b=>2}'))
        self.assertEqual({}, self.eval('{}'))

    def test_dict_from_sequence(self):
        self.assertEqual({'a': 1, 'b': 2},
                         self.eval("dict(list(list(a, 1), list('b', 2)))"))

        generator = (i for i in (('a', 1), ['b', 2]))
        self.assertEqual({'a': 1, 'b': 2},
                         self.eval('dict($)', data=generator))

    def test_to_dict(self):
        self.assertEqual({1: 1, 2: 4, 3: 9},
                         self.eval('$.toDict($, $*$)', data=[1, 2, 3]))

    def test_keyword_dict_access(self):
        data = {'A': 12, 'b c': 44, '__d': 99, '_e': 999}
        self.assertEqual(12, self.eval('$.A', data=data))
        self.assertEqual(999, self.eval('$._e', data=data))

        self.assertRaises(exceptions.NoMatchingFunctionException,
                          self.eval, "$.'b c'", data=data)
        self.assertRaises(exceptions.NoMatchingFunctionException,
                          self.eval, '$.123', data=data)
        self.assertRaises(KeyError, self.eval, '$.b', data=data)
        self.assertRaises(
            exceptions.YaqlLexicalException,
            self.eval, '$.__d', data=data)

    def test_indexer_dict_access(self):
        data = {'a': 12, 'b c': 44}
        self.assertEqual(12, self.eval('$[a]', data=data))
        self.assertEqual(44, self.eval("$['b c']", data=data))
        self.assertRaises(KeyError,
                          self.eval, "$[b]", data=data)

    def test_indexer_dict_access_with(self):
        data = {'a': 12, 'b c': 44}
        self.assertEqual(55, self.eval('$[c, 55]', data=data))
        self.assertEqual(66, self.eval('$[c, default => 66]', data=data))

    def test_list_eq(self):
        self.assertTrue(self.eval('[c, 55]=[c, 55]'))
        self.assertFalse(self.eval('[c, 55]=[55, c]'))
        self.assertFalse(self.eval('[c, 55]=null'))
        self.assertFalse(self.eval('null = [c, 55]'))

    def test_list_neq(self):
        self.assertFalse(self.eval('[c, 55] != [c, 55]'))
        self.assertTrue(self.eval('[c, 55] != [55, c]'))
        self.assertTrue(self.eval('[c, 55] != null'))
        self.assertTrue(self.eval('null != [c, 55]'))

    def test_dict_eq(self):
        self.assertTrue(self.eval('{a => [c, 55]} = {a => [c, 55]}'))
        self.assertTrue(self.eval('{[c, 55] => a} = {[c, 55] => a}'))
        self.assertFalse(self.eval('{[c, 55] => a} = {[c, 56] => a}'))
        self.assertFalse(self.eval('{[c, 55] => a, b => 1} = {[c, 55] => a}'))
        self.assertFalse(self.eval('{[c, 55] => a} = null'))

    def test_dict_neq(self):
        self.assertFalse(self.eval('{a => [c, 55]} != {a => [c, 55]}'))
        self.assertFalse(self.eval('{[c, 55] => a} != {[c, 55] => a}'))
        self.assertTrue(self.eval('{[c, 55] => a} != {[c, 56] => a}'))
        self.assertTrue(self.eval('{[c, 55] => a, b => 1} != {[c, 55] => a}'))
        self.assertTrue(self.eval('{[c, 55] => a} != null'))

    def test_dict_get(self):
        data = {'a': 12, 'b c': 44}
        self.assertEqual(12, self.eval('$.get(a)', data=data))
        self.assertIsNone(self.eval('$.get(b)', data=data))
        self.assertEqual(50, self.eval('$.get(c, 50)', data=data))

    def test_dict_set(self):
        data = {'a': 12, 'b c': 44}
        self.assertEqual(
            {'a': 99, 'b c': 44, 'x': None},
            self.eval('$.set(a, 99).set(x, null)', data=data))
        self.assertEqual(data, {'a': 12, 'b c': 44})

    def test_dict_set_many(self):
        data = {'a': 12, 'b c': 44}
        self.assertEqual(
            {'a': 55, 'b c': 44, 'd x': 99, None: None},
            self.eval('$.set(dict(a => 55, "d x" => 99, null => null))',
                      data=data))
        self.assertEqual(data, {'a': 12, 'b c': 44})

    def test_dict_set_many_inline(self):
        data = {'a': 12, 'b c': 44}
        self.assertEqual(
            {'a': 55, 'b c': 44, 'd x': 99},
            self.eval('$.set(a => 55, "d x" => 99)', data=data))
        self.assertEqual(data, {'a': 12, 'b c': 44})

    def test_dict_keys(self):
        data = {'a': 12, 'b': 44}
        self.assertCountEqual(['a', 'b'], self.eval('$.keys()', data=data))

    def test_dict_values(self):
        data = {'a': 12, 'b': 44}
        self.assertCountEqual([12, 44], self.eval('$.values()', data=data))

    def test_dict_items(self):
        data = {'a': 12, 'b': 44}
        self.assertCountEqual([['a', 12], ['b', 44]],
                              self.eval('$.items()', data=data))
        self.assertEqual(data, self.eval('dict($.items())', data=data))

    def test_in(self):
        data = {'a': 12, 'b': 44}
        self.assertTrue(self.eval('44 in $.values()', data=data))
        self.assertTrue(self.eval('24 in $.values().select(2*$)', data=data))
        self.assertTrue(self.eval('{a => 2} in {{a => 2} => {b => 3}}.keys()'))
        self.assertTrue(self.eval('5 in set(1, 2, 5)'))
        self.assertTrue(self.eval('[1, 2] in set([1, 2], 5)'))
        self.assertTrue(self.eval('5 in [1, 2, 5]'))
        self.assertTrue(self.eval('[1, 2] in {[1, 2] => [3, 4]}.keys()'))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'a in $', data=data)

    def test_contains(self):
        data = {'a': 12, 'b': 44}
        self.assertTrue(self.eval('$.containsKey(a)', data=data))
        self.assertTrue(self.eval('$.values().contains(44)', data=data))
        self.assertFalse(self.eval('$.containsKey(null)', data=data))
        self.assertTrue(self.eval(
            '$.values().select(2*$).contains(24)', data=data))
        self.assertTrue(self.eval('set(1, 2, 5).contains(5)'))
        self.assertTrue(self.eval('[1, 2, 5].contains(5)'))
        self.assertTrue(
            self.eval('{{a => 2} => {b => 3}}.containsKey({a => 2})'))
        self.assertTrue(self.eval('{[1, 2] => [3, 4]}.containsKey([1, 2])'))
        self.assertTrue(self.eval('{[1, 2] => [3, 4]}.containsValue([3, 4])'))
        self.assertTrue(self.eval('set([1, 2], 5).contains([1, 2])'))

    def test_list_addition(self):
        self.assertEqual(
            [1, 2, 3, 4],
            self.eval('list(1, 2) + list(3, 4)'))
        self.assertEqual(
            [1, 2, 6, 8],
            self.eval('list(1, 2) + list(3, 4).select($ * 2)'))

    def test_dict_addition(self):
        self.assertEqual(
            {'a': 1, 'b': 2},
            self.eval('dict(a => 1) + dict(b => 2)'))

    def test_list_multiplication(self):
        self.assertCountEqual(
            [1, 2, 1, 2, 1, 2],
            self.eval('3 * [1, 2]'))

        self.assertCountEqual(
            [1, 2, 1, 2, 1, 2],
            self.eval('[1, 2] * 3'))

    def test_dict_list_key(self):
        self.assertEqual(
            3,
            self.eval('dict($ => 3).get($)', data=[1, 2]))

        self.assertEqual(
            3,
            self.eval('dict($ => 3).get($)', data=[1, [2]]))

    def test_dict_dict_key(self):
        self.assertEqual(
            3,
            self.eval('dict($ => 3).get($)', data={'a': 1}))

    def test_delete(self):
        self.assertEqual(
            [2, 3, 4],
            self.eval('[1, 2, 3, 4].delete(0)'))

        self.assertEqual(
            [3, 4],
            self.eval('[1, 2, 3, 4].delete(0, 2)'))

        self.assertEqual(
            [4],
            self.eval('[1, 2, 3, 4].delete(0, 2).delete(0)'))

        self.assertEqual(
            [1],
            self.eval('[1, 2, 3, 4].delete(1, -1)'))

        self.assertEqual(
            [1, 2, 3, 4],
            self.eval('[1, 2, 3, 4].delete(0, 0)'))

        self.assertEqual(
            [],
            self.eval('[1, 2, 3, 4].delete(0, -1)'))

    def test_insert(self):
        self.assertEqual(
            [1, 'a', 2],
            self.eval('[1, 2].insert(1, a)'))

        self.assertEqual(
            [1, ['a', 'b'], 2],
            self.eval('[1, 2].insert(1, [a, b])'))

        self.assertEqual(
            [1, 'a', 2],
            self.eval('[1, 2].insert(-1, a)'))

        self.assertEqual(
            [1, 2, 'a'],
            self.eval('[1, 2].insert(100, a)'))

        self.assertEqual(
            ['b', 'a'],
            self.eval('[].insert(0, a).insert(0, b)'))

        self.assertRaises(
            exceptions.NoMatchingMethodException,
            self.eval, 'set(a, b).insert(1, a)')

    def test_insert_iter(self):
        self.assertEqual(
            [1, 'a', 2],
            self.eval('[1, 2].select($).insert(1, a)'))

        self.assertEqual(
            [1, ['a', 'b'], 2],
            self.eval('[1, 2].select($).insert(1, [a, b])'))

        self.assertEqual(
            [1, 2],
            self.eval('[1, 2].select($).insert(-1, a)'))

        self.assertEqual(
            [1, 2, 'a'],
            self.eval('[1, 2].select($).insert(100, a)'))

        self.assertEqual(
            ['b', 'a'],
            self.eval('[].select($).insert(0, a).insert(0, b)'))

        self.assertEqual(
            ['a', 'a', 'b'],
            self.eval('set(a, b).orderBy($).insert(1, a)'))

    def test_insert_many(self):
        self.assertEqual(
            [1, 'a', 'b', 2],
            self.eval('[1, 2].insertMany(1, [a, b])'))

        self.assertEqual(
            ['a', 'b', 1, 2],
            self.eval('[1, 2].insertMany(-1, [a, b])'))

        self.assertEqual(
            [1, 2, 'a', 'b'],
            self.eval('[1, 2].insertMany(100, [a, b])'))

        self.assertEqual(
            ['a', 'a', 'b', 'b'],
            self.eval('[].insertMany(0, [a, b]).insertMany(1, [a, b])'))

    def test_replace(self):
        self.assertEqual(
            [None, 2, 3, 4],
            self.eval('[1, 2, 3, 4].replace(0, null)'))

        self.assertEqual(
            [None, 3, 4],
            self.eval('[1, 2, 3, 4].replace(0, null, 2)'))

        self.assertEqual(
            [1, 7],
            self.eval('[1, 2, 3, 4].replace(1, 7, -1)'))

        self.assertEqual(
            7,
            self.eval('set(1, 2, 3, 4).replace(1, 7)')[1])

        self.assertEqual(
            [1, 7, 3, 4],
            self.eval('set(4, 2, 3, 1).orderBy($).replace(1, 7)'))

    def test_replace_many(self):
        self.assertEqual(
            [7, 8, 2, 3, 4],
            self.eval('[1, 2, 3, 4].replaceMany(0, [7, 8])'))

        self.assertEqual(
            [7, 8, 3, 4],
            self.eval('[1, 2, 3, 4].replaceMany(0, [7, 8], 2)'))

        self.assertEqual(
            [1, 7, 8],
            self.eval('[1, 2, 3, 4].replaceMany(1, [7, 8], -1)'))

    def test_delete_dict(self):
        data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        self.assertEqual(
            {'a': 1, 'd': 4},
            self.eval('$.delete(b, c)', data=data))

    def test_delete_all(self):
        data = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        self.assertEqual(
            {'a': 1, 'd': 4},
            self.eval('$.deleteAll([b, c])', data=data))

    def test_set(self):
        self.assertCountEqual([2, 1, 3], self.eval('set(1, 2, 3, 2, 1)'))
        self.assertEqual([[1, 2, 3, 2, 1]], self.eval('set([1, 2, 3, 2, 1])'))
        self.assertEqual([], self.eval('set()'))
        self.assertEqual(
            [{'a': {'b': 'c'}}],
            self.eval('set({a => {b => c}})'))

    def test_set_from_iterator(self):
        self.assertCountEqual([2, 1, 3], self.eval('set([1, 2, 3].select($))'))

    def test_to_set(self):
        self.assertCountEqual(
            [2, 1, 3], self.eval('[1, 2, 3].select($).toSet()'))

        self.assertCountEqual(
            [2, 1, 3], self.eval('[1, 2, 3].toSet()'))

    def test_set_len(self):
        self.assertEqual(3, self.eval('set(1, 2, 3).len()'))
        self.assertEqual(3, self.eval('len(set(1, 2, 3))'))

    def test_set_addition(self):
        self.assertCountEqual(
            [4, 3, 2, 1],
            self.eval('set(1, 2, 3) + set(4, 2, 3)'))

        self.assertTrue(
            self.eval('isSet(set(1, 2, 3) + set(4, 2, 3))'))

    def test_set_union(self):
        self.assertCountEqual(
            [4, 3, 2, 1],
            self.eval('set(1, 2, 3).union(set(4, 2, 3))'))

    def test_set_eq(self):
        self.assertTrue(self.eval('set(1, 2, 3) = set(3, 2, 1)'))
        self.assertFalse(self.eval('set(1, 2, 3) = set(1, 2, 3, 4)'))

    def test_set_neq(self):
        self.assertFalse(self.eval('set(1, 2, 3) != set(3, 2, 1)'))
        self.assertTrue(self.eval('set(1, 2, 3) != set(1, 2, 3, 4)'))

    def test_set_lt(self):
        self.assertTrue(self.eval('set(1, 2, 3) < set(1, 2, 3, 4)'))
        self.assertFalse(self.eval('set(1, 2, 3) < set(1, 2, 5)'))

    def test_set_gt(self):
        self.assertTrue(self.eval('set(1, 2, 3, 4) > set(1, 2, 3)'))
        self.assertFalse(self.eval('set(1, 2, 3) > set(1, 2, 3)'))

    def test_set_gte(self):
        self.assertFalse(self.eval('set(1, 2, 4) >= set(1, 2, 3)'))
        self.assertTrue(self.eval('set(1, 2, 3) >= set(1, 2, 3)'))

    def test_set_lte(self):
        self.assertFalse(self.eval('set(1, 2, 3) <= set(1, 2, 4)'))
        self.assertTrue(self.eval('set(1, 2, 3) <= set(1, 2, 3)'))

    def test_set_difference(self):
        self.assertCountEqual(
            [4, 1],
            self.eval('set(1, 2, 3, 4).difference(set(2, 3))'))

    def test_set_subtraction(self):
        self.assertCountEqual(
            [4, 1],
            self.eval('set(1, 2, 3, 4) - set(2, 3)'))

        self.assertTrue(
            self.eval('isSet(set(1, 2, 3, 4) - set(2, 3))'))

    def test_set_symmetric_difference(self):
        self.assertCountEqual(
            [4, 1, 5],
            self.eval('set(1, 2, 3, 4).symmetricDifference(set(2, 3, 5))'))

    def test_set_add(self):
        self.assertCountEqual(
            [4, 1, 2, 3],
            self.eval('set(1, 2, 3).add(4)'))

        self.assertCountEqual(
            [4, 1, 2, 3, 5],
            self.eval('set(1, 2, 3).add(4, 5)'))

        self.assertCountEqual(
            [1, 3, 2, [1, 2]],
            self.eval('set(1, 2, 3).add([1, 2])'))

        self.assertCountEqual(
            [4, 1, None, 2, 3, 5],
            self.eval('set(1, 2, 3).add(4, 5, null)'))

        self.assertTrue(
            self.eval('isSet(set(1, 2, 3).add(4, 5, null))'))

    def test_set_remove(self):
        self.assertCountEqual(
            [1, 3],
            self.eval('set(1, 2, 3).remove(2)'))

        self.assertCountEqual(
            [3, None],
            self.eval('set(1, 2, null, 3).remove(1, 2, 5)'))

        self.assertCountEqual(
            [3],
            self.eval('set(1, 2, null, 3).remove(1, 2, 5, null)'))

        self.assertCountEqual(
            [1, 3, 2],
            self.eval('set(1, 2, 3, [1, 2]).remove([1, 2])'))

        self.assertTrue(
            self.eval('isSet(set(1, 2, 3, [1, 2]).remove([1, 2]))'))
