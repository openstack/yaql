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


class TestQueries(yaql.tests.TestCase):
    def test_where(self):
        data = [1, 2, 3, 4, 5, 6]
        self.assertEqual([4, 5, 6], self.eval('$.where($ > 3)', data=data))

    def test_select(self):
        data = [1, 2, 3]
        self.assertEqual([1, 4, 9], self.eval('$.select($ * $)', data=data))

    def test_keyword_collection_access(self):
        data = [{'a': 2}, {'a': 4}]
        self.assertEqual([2, 4], self.eval('$.a', data=data))
        self.assertEqual([2, 4], self.eval('$.select($).a', data=data))

    def test_skip(self):
        data = [1, 2, 3, 4]
        self.assertEqual([2, 3, 4], self.eval('$.skip(1)', data=data))

    def test_limit(self):
        data = [1, 2, 3, 4]
        self.assertEqual([1, 2], self.eval('$.limit(2)', data=data))
        self.assertEqual([1, 2], self.eval('$.take(2)', data=data))

    def test_append(self):
        data = [1, 2]
        self.assertEqual([1, 2, 3, 4], self.eval('$.append(3, 4)', data=data))

    def test_complex_query(self):
        data = [1, 2, 3, 4, 5, 6]
        self.assertEqual(
            [4],
            self.eval('$.where($ < 4).select($ * $).skip(1).limit(1)',
                      data=data))

    def test_distinct(self):
        data = [1, 2, 3, 2, 4, 8]
        self.assertEqual([1, 2, 3, 4, 8], self.eval('$.distinct()', data=data))
        self.assertEqual([1, 2, 3, 4, 8], self.eval('distinct($)', data=data))

    def test_distinct_structures(self):
        data = [{'a': 1}, {'b': 2}, {'a': 1}]
        self.assertEqual(
            [{'a': 1}, {'b': 2}],
            self.eval('$.distinct()', data=data))

    def test_distinct_with_selector(self):
        data = [['a', 1], ['b', 2], ['c', 1], ['d', 3], ['e', 2]]
        self.assertCountEqual([['a', 1], ['b', 2], ['d', 3]],
                              self.eval('$.distinct($[1])', data=data))
        self.assertCountEqual([['a', 1], ['b', 2], ['d', 3]],
                              self.eval('distinct($, $[1])', data=data))

    def test_any(self):
        self.assertFalse(self.eval('$.any()', data=[]))
        self.assertTrue(self.eval('$.any()', data=[0]))

    def test_all(self):
        self.assertTrue(self.eval('$.all()', data=[]))
        self.assertFalse(self.eval('$.all()', data=[1, 0]))
        self.assertTrue(self.eval('$.all()', data=[1, 2]))
        self.assertFalse(self.eval('$.all($ > 1)', data=[2, 1]))
        self.assertTrue(self.eval('$.all($ > 1)', data=[2, 3]))

    def test_enumerate(self):
        data = [1, 2, 3]
        self.assertEqual([[0, 1], [1, 2], [2, 3]],
                         self.eval('$.enumerate()', data=data))
        self.assertEqual([[3, 1], [4, 2], [5, 3]],
                         self.eval('$.enumerate(3)', data=data))
        self.assertEqual([[0, 1], [1, 2], [2, 3]],
                         self.eval('enumerate($)', data=data))
        self.assertEqual([[3, 1], [4, 2], [5, 3]],
                         self.eval('enumerate($, 3)', data=data))

    def test_concat(self):
        data = [1, 2, 3]
        self.assertEqual(
            [1, 2, 3, 2, 4, 6],
            self.eval('$.select($).concat($.select(2 * $))', data=data))
        self.assertEqual(
            [1, 2, 3, 2, 4, 6, 1, 2, 3],
            self.eval('concat($, $.select(2 * $), $)', data=data))

    def test_len(self):
        data = [1, 2, 3]
        self.assertEqual(3, self.eval('len($)', data=data))
        self.assertEqual(3, self.eval('$.len()', data=data))
        self.assertEqual(3, self.eval('$.count()', data=data))
        self.assertRaises(
            exceptions.FunctionResolutionError,
            self.eval, 'count($)', data=data)

    def test_sum(self):
        data = range(4)
        self.assertEqual(6, self.eval('$.sum()', data=data))
        self.assertEqual(106, self.eval('$.sum(100)', data=data))
        self.assertEqual(100, self.eval('[].sum(100)'))

    def test_memorize(self):
        generator_func = lambda: (i for i in range(3))  # noqa: E731
        self.assertRaises(
            TypeError,
            self.eval, '$.len() + $.sum()', data=generator_func())

        self.assertEqual(
            6,
            self.eval('let($.memorize()) -> $.len() + $.sum()',
                      data=generator_func()))

    def test_first(self):
        self.assertEqual(2, self.eval('list(2, 3).first()'))
        self.assertEqual(4, self.eval('list(2, 3).select($ * 2).first()'))
        self.assertIsNone(self.eval('list().first(null)'))
        self.assertRaises(StopIteration, self.eval, 'list().first()')
        self.assertEqual(99, self.eval('list().first(99)'))

    def test_single(self):
        self.assertEqual(2, self.eval('list(2).single()'))
        self.assertRaises(StopIteration, self.eval, 'list().single()')
        self.assertRaises(StopIteration, self.eval, 'list(1, 2).single()')

    def test_last(self):
        self.assertEqual(3, self.eval('list(2, 3).last()'))
        self.assertEqual(6, self.eval('list(2, 3).select($ * 2).last()'))
        self.assertIsNone(self.eval('list().last(null)'))
        self.assertEqual(99, self.eval('list().last(99)'))
        self.assertRaises(StopIteration, self.eval, 'list().last()')

    def test_range(self):
        self.assertEqual([0, 1], self.eval('range(2)'))
        self.assertEqual([1, 2, 3], self.eval('range(1, 4)'))
        self.assertEqual([4, 3, 2], self.eval('range(4, 1, -1)'))

    def test_select_many(self):
        self.assertEqual([0, 0, 1, 0, 1, 2],
                         self.eval('range(4).selectMany(range($))'))

    def test_select_many_scalar(self):
        # check that string is not interpreted as a sequence and that
        # selectMany works when selector returns scalar
        self.assertEqual(
            ['xx', 'xx'],
            self.eval('range(2).selectMany(xx)'))

    def test_order_by(self):
        self.assertEqual(
            [1, 2, 3, 4],
            self.eval('$.orderBy($)', data=[4, 2, 1, 3]))

        self.assertEqual(
            [4, 3, 2, 1],
            self.eval('$.orderByDescending($)', data=[4, 2, 1, 3]))

    def test_order_by_multilevel(self):
        self.assertEqual(
            [[1, 0], [1, 5], [2, 2]],
            self.eval(
                '$.orderBy($[0]).thenBy($[1])',
                data=[[2, 2], [1, 5], [1, 0]]))

        self.assertEqual(
            [[1, 5], [1, 0], [2, 2]],
            self.eval(
                '$.orderBy($[0]).thenByDescending($[1])',
                data=[[2, 2], [1, 5], [1, 0]]))

        self.assertEqual(
            [[2, 2], [1, 0], [1, 5]],
            self.eval(
                '$.orderByDescending($[0]).thenBy($[1])',
                data=[[2, 2], [1, 5], [1, 0]]))

        self.assertEqual(
            [[2, 2], [1, 5], [1, 0]],
            self.eval(
                '$.orderByDescending($[0]).thenByDescending($[1])',
                data=[[2, 2], [1, 5], [1, 0]]))

    def test_group_by(self):
        data = {'a': 1, 'b': 2, 'c': 1, 'd': 3, 'e': 2}
        self.assertCountEqual(
            [
                [1, [['a', 1], ['c', 1]]],
                [2, [['b', 2], ['e', 2]]],
                [3, [['d', 3]]]
            ],
            self.eval('$.items().orderBy($[0]).groupBy($[1])', data=data))

        self.assertCountEqual(
            [[1, ['a', 'c']], [2, ['b', 'e']], [3, ['d']]],
            self.eval('$.items().orderBy($[0]).groupBy($[1], $[0])',
                      data=data))

        self.assertCountEqual(
            [[1, 'ac'], [2, 'be'], [3, 'd']],
            self.eval('$.items().orderBy($[0]).'
                      'groupBy($[1], $[0], $.sum())', data=data))

        self.assertCountEqual(
            [[1, ['a', 1, 'c', 1]], [2, ['b', 2, 'e', 2]], [3, ['d', 3]]],
            self.eval('$.items().orderBy($[0]).'
                      'groupBy($[1],,  $.sum())',
                      data=data))

        self.assertCountEqual(
            [[1, ['a', 1, 'c', 1]], [2, ['b', 2, 'e', 2]], [3, ['d', 3]]],
            self.eval('$.items().orderBy($[0]).'
                      'groupBy($[1], aggregator => $.sum())',
                      data=data))

    def test_group_by_old_syntax(self):
        # Test the syntax used in 1.1.1 and earlier, where the aggregator
        # function was passed the key as well as the value list, and returned
        # the key along with the aggregated value. This ensures backward
        # compatibility with existing expressions.
        data = {'a': 1, 'b': 2, 'c': 1, 'd': 3, 'e': 2}

        self.assertCountEqual(
            [[1, 'ac'], [2, 'be'], [3, 'd']],
            self.eval('$.items().orderBy($[0]).'
                      'groupBy($[1], $[0], [$[0], $[1].sum()])', data=data))

        self.assertCountEqual(
            [[1, ['a', 1, 'c', 1]], [2, ['b', 2, 'e', 2]], [3, ['d', 3]]],
            self.eval('$.items().orderBy($[0]).'
                      'groupBy($[1],,  [$[0], $[1].sum()])',
                      data=data))

        self.assertCountEqual(
            [[1, ['a', 1, 'c', 1]], [2, ['b', 2, 'e', 2]], [3, ['d', 3]]],
            self.eval('$.items().orderBy($[0]).'
                      'groupBy($[1], aggregator => [$[0], $[1].sum()])',
                      data=data))

    def test_join(self):
        self.assertEqual(
            [[2, 1], [3, 1], [3, 2], [4, 1], [4, 2], [4, 3]],
            self.eval('$.join($, $1 > $2, [$1, $2])', data=[1, 2, 3, 4]))

        self.assertEqual(
            [[1, 3], [1, 4], [2, 3], [2, 4]],
            self.eval('[1,2].join([3, 4], true, [$1, $2])'))

    def test_zip(self):
        self.assertEqual(
            [[1, 4], [2, 5]],
            self.eval('[1, 2, 3].zip([4, 5])'))

        self.assertEqual(
            [[1, 4, 6], [2, 5, 7]],
            self.eval('[1, 2, 3].zip([4, 5], [6, 7, 8])'))

    def test_zip_longest(self):
        self.assertEqual(
            [[1, 4], [2, 5], [3, None]],
            self.eval('[1, 2, 3].zipLongest([4, 5])'))

        self.assertEqual(
            [[1, 4, 6], [2, 5, None], [3, None, None]],
            self.eval('[1, 2, 3].zipLongest([4, 5], [6])'))

        self.assertEqual(
            [[1, 4], [2, 5], [3, 0]],
            self.eval('[1, 2, 3].zipLongest([4, 5], default => 0)'))

    def test_repeat(self):
        self.assertEqual(
            [None, None],
            self.eval('null.repeat(2)'))

        self.assertEqual(
            [1, 1, 1, 1, 1],
            self.eval('1.repeat().limit(5)'))

    def test_cycle(self):
        self.assertEqual(
            [1, 2, 1, 2, 1],
            self.eval('[1, 2].cycle().take(5)'))

    def test_take_while(self):
        self.assertEqual(
            [1, 2, 3],
            self.eval('[1, 2, 3, 4, 5].takeWhile($ < 4)'))

    def test_skip_while(self):
        self.assertEqual(
            [4, 5],
            self.eval('[1, 2, 3, 4, 5].skipWhile($ < 4)'))

    def test_index_of(self):
        self.assertEqual(1, self.eval('[1, 2, 3, 2, 1].indexOf(2)'))
        self.assertEqual(-1, self.eval('[1, 2, 3, 2, 1].indexOf(22)'))

    def test_last_index_of(self):
        self.assertEqual(3, self.eval('[1, 2, 3, 2, 1].lastIndexOf(2)'))
        self.assertEqual(-1, self.eval('[1, 2, 3, 2, 1].lastIndexOf(22)'))

    def test_index_where(self):
        self.assertEqual(1, self.eval('[1, 2, 3, 2, 1].indexWhere($ = 2)'))
        self.assertEqual(-1, self.eval('[1, 2, 3, 2, 1].indexWhere($ = 22)'))

    def test_last_index_where(self):
        self.assertEqual(3, self.eval('[1, 2, 3, 2, 1].lastIndexWhere($ = 2)'))
        self.assertEqual(
            -1, self.eval('[1, 2, 3, 2, 1].lastIndexWhere($ = 22)'))

    def test_slice(self):
        self.assertEqual(
            [[1, 2], [3, 4], [5]],
            self.eval('range(1, 6).slice(2)'))
        self.assertEqual(
            [[1, 2], [3, 4], [5]],
            self.eval('[1,2,3,4,5].slice(2)'))

    def test_split_where(self):
        self.assertEqual(
            [[], [2, 3], [5]],
            self.eval('range(1, 6).splitWhere($ mod 3 = 1)'))

    def test_split_at(self):
        self.assertEqual(
            [[1, 2], [3, 4, 5]],
            self.eval('range(1, 6).splitAt(2)'))

    def test_slice_where(self):
        self.assertEqual(
            [['a', 'a'], ['b'], ['a', 'a']],
            self.eval('[a,a,b,a,a].sliceWhere($ != a)'))

    def test_aggregate(self):
        self.assertEqual(
            'aabaa',
            self.eval('[a,a,b,a,a].aggregate($1 + $2)'))

        self.assertRaises(
            TypeError,
            self.eval, '[].aggregate($1 + $2)')

        self.assertEqual(
            1,
            self.eval('[].aggregate($1 + $2, 1)'))

        self.assertEqual(
            'aabaa',
            self.eval('[a,a,b,a,a].reduce($1 + $2)'))

        self.assertEqual(
            0,
            self.eval('[].reduce(max($1, $2), 0)'))

    def test_accumulate(self):
        self.assertEqual(
            ['a', 'aa', u'aab', 'aaba', 'aabaa'],
            self.eval('[a,a,b,a,a].accumulate($1 + $2)'))

        self.assertEqual(
            [1],
            self.eval('[].accumulate($1 + $2, 1)'))

    def test_default_if_empty(self):
        self.assertEqual(
            [1, 2],
            self.eval('[].defaultIfEmpty([1, 2])'))

        self.assertEqual(
            [3, 4],
            self.eval('[3, 4].defaultIfEmpty([1, 2])'))

        self.assertEqual(
            [1, 2],
            self.eval('[].select($).defaultIfEmpty([1, 2])'))

        self.assertEqual(
            [3, 4],
            self.eval('[3, 4].select($).defaultIfEmpty([1, 2])'))

    def test_generate(self):
        self.assertEqual(
            [0, 2, 4, 6, 8],
            self.eval('generate(0, $ < 10, $ + 2)'))

        self.assertEqual(
            [0, 4, 16, 36, 64],
            self.eval('generate(0, $ < 10, $ + 2, $ * $)'))

    def test_generate_many(self):
        friends = {
            'John': ['Jim'],
            'Jim': ['Jay', 'Jax'],
            'Jax': ['John', 'Jacob', 'Jonathan'],
            'Jacob': ['Jonathan', 'Jenifer'],
        }
        self.assertEqual(
            ['John', 'Jim', 'Jay', 'Jax', 'Jacob', 'Jonathan', 'Jenifer'],
            self.eval(
                'generateMany(John, $data.get($, []), decycle => true)',
                friends))

        self.assertEqual(
            ['John', 'Jim', 'Jay', 'Jax', 'Jacob', 'Jonathan', 'Jenifer'],
            self.eval(
                'generateMany(John, $data.get($, []), '
                'decycle => true, depthFirst => true)', friends))

        self.assertEqual(
            ['Jay'],
            self.eval('generateMany(Jay, $data.get($, []))', friends))

        self.assertEqual(
            ['JAX', 'JOHN', 'JACOB', 'JONATHAN', 'JIM', 'JENIFER', 'JAY'],
            self.eval(
                'generateMany(Jax, $data.get($, []), $.toUpper(), '
                'decycle => true)', friends))

    def test_max(self):
        self.assertEqual(
            0,
            self.eval('[].max(0)'))

        self.assertRaises(
            TypeError,
            self.eval, '[].max()')

        self.assertEqual(
            234,
            self.eval('[44, 234, 23].max()'))

    def test_min(self):
        self.assertEqual(
            0,
            self.eval('[].min(0)'))

        self.assertRaises(
            TypeError,
            self.eval, '[].min()')

        self.assertEqual(
            23,
            self.eval('[44, 234, 23].min()'))

    def test_reverse(self):
        self.assertEqual(
            [9, 4, 1],
            self.eval('range(1, 4).select($*$).reverse()'))

    def test_merge_with(self):
        dict1 = {'a': 1, 'b': 'x', 'c': [1, 2], 'x': {'a': 1}}
        dict2 = {'d': 5, 'b': 'y', 'c': [2, 3], 'x': {'b': 2}}
        self.assertEqual(
            {'a': 1, 'c': [1, 2, 3], 'b': 'y', 'd': 5, 'x': {'a': 1, 'b': 2}},
            self.eval(
                '$.d1.mergeWith($.d2)',
                data={'d1': dict1, 'd2': dict2}))

        dict1 = {'a': 1, 'b': 2, 'c': [1, 2]}
        dict2 = {'d': 5, 'b': 3, 'c': [2, 3]}
        self.assertEqual(
            {'a': 1, 'c': [1, 2, 2, 3], 'b': 3, 'd': 5},
            self.eval(
                '$.d1.mergeWith($.d2, $1 + $2)',
                data={'d1': dict1, 'd2': dict2}))

        self.assertEqual(
            {'a': 1, 'b': 3, 'c': [2, 3], 'd': 5},
            self.eval(
                '$.d1.mergeWith($.d2, $1 + $2, maxLevels => 1)',
                data={'d1': dict1, 'd2': dict2}))

        self.assertEqual(
            {'a': 1, 'b': 2, 'c': [1, 2, 3], 'd': 5},
            self.eval(
                '$.d1.mergeWith($.d2,, min($1, $2))',
                data={'d1': dict1, 'd2': dict2}))

    def test_is_iterable(self):
        self.assertEqual(
            True,
            self.eval('isIterable([])'))
        self.assertEqual(
            True,
            self.eval('isIterable([1,2])'))
        self.assertEqual(
            True,
            self.eval('isIterable(set(1,2))'))
        self.assertEqual(
            False,
            self.eval('isIterable(1)'))
        self.assertEqual(
            False,
            self.eval('isIterable("foo")'))
        self.assertEqual(
            False,
            self.eval('isIterable({"a" => 1})'))

    def test_infinite_collections(self):
        self.assertRaises(
            exceptions.CollectionTooLargeException,
            self.eval, 'len(list(sequence()))')

        self.assertRaises(
            exceptions.CollectionTooLargeException,
            self.eval, 'list(sequence())')

        self.assertRaises(
            exceptions.CollectionTooLargeException,
            self.eval, 'len(dict(sequence().select([$, $])))')

        self.assertRaises(
            exceptions.CollectionTooLargeException,
            self.eval, 'dict(sequence().select([$, $]))')

        self.assertRaises(
            exceptions.CollectionTooLargeException,
            self.eval, 'sequence()')

        self.assertRaises(
            exceptions.CollectionTooLargeException,
            self.eval, 'set(sequence())')
