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


class TestSystem(yaql.tests.TestCase):
    def test_def(self):
        self.assertEqual(
            [1, 4, 9],
            self.eval('def(sq, $*$) -> $.select(sq($))', data=[1, 2, 3]))
        self.assertEqual(
            [1, 4, 9],
            self.eval('def(sq, $arg * $arg) -> $.select(sq(arg => $))',
                      data=[1, 2, 3]))

    def test_def_recursion(self):
        self.assertEqual(24, self.eval(
            'def(rec, switch($ = 1 => 1, true => $*rec($-1))) -> rec($)',
            data=4))

    def test_elvis_dict(self):
        self.assertEqual(1, self.eval('$?.a', data={'a': 1}))
        self.assertIsNone(self.eval('$?.a', data=None))

    def test_elvis_method(self):
        self.assertEqual([2, 3], self.eval('$?.select($+1)', data=[1, 2]))
        self.assertIsNone(self.eval('$?.select($+1)', data=None))

    def test_unpack(self):
        self.assertEqual(
            5, self.eval('[2, 3].unpack() -> $1 + $2'))

    def test_unpack_with_names(self):
        self.assertEqual(
            5, self.eval('[2, 3].unpack(a, b) -> $a + $b'))

        self.assertRaises(
            ValueError,
            self.eval, '[2, 3].unpack(a, b, c) -> $a + $b')

        self.assertRaises(
            ValueError,
            self.eval, '[2, 3].unpack(a) -> $a')

    def test_assert(self):
        self.assertEqual(
            [3, 4],
            self.eval('[2, 3].assert(len($) > 1).select($ + 1)'))

        self.assertRaises(
            AssertionError,
            self.eval, '[2].assert(len($) > 1).select($ + 1)')

        self.assertEqual(
            3,
            self.eval('[2].select($ + 1).assert(len($) = 1).first()'))
