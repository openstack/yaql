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
from yaql.language import specs
from yaql.language import yaqltypes
import yaql.tests


class TestMiscellaneous(yaql.tests.TestCase):
    def test_pass_lambda_from_code(self):
        self.assertEqual(
            [],
            list(self.context('where', self.engine, [1, 2, 3])(False))
        )
        self.assertEqual(
            [2, 3],
            list(self.context('where', self.engine, [1, 2, 3])(
                lambda t: t > 1))
        )

    def test_bool_is_not_an_integer(self):
        @specs.parameter('arg', yaqltypes.Integer())
        def foo(arg):
            return arg

        self.context.register_function(foo)
        self.assertEqual(2, self.eval('foo(2)'))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo(true)')

    def test_nullable_collections(self):
        @specs.parameter('arg', yaqltypes.Sequence())
        def foo1(arg):
            return arg is None

        @specs.parameter('arg', yaqltypes.Sequence(nullable=True))
        def foo2(arg):
            return arg is None

        @specs.parameter('arg', yaqltypes.Iterable())
        def bar1(arg):
            return arg is None

        @specs.parameter('arg', yaqltypes.Iterable(nullable=True))
        def bar2(arg):
            return arg is None

        @specs.parameter('arg', yaqltypes.Iterator())
        def baz1(arg):
            return arg is None

        @specs.parameter('arg', yaqltypes.Iterator(nullable=True))
        def baz2(arg):
            return arg is None

        for func in (foo1, foo2, bar1, bar2, baz1, baz2):
            self.context.register_function(func)

        self.assertFalse(self.eval('foo1([1, 2])'))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo1(null)')
        self.assertFalse(self.eval('foo2([1, 2])'))
        self.assertTrue(self.eval('foo2(null)'))

        self.assertFalse(self.eval('bar1([1, 2])'))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'bar1(null)')
        self.assertFalse(self.eval('bar2([1, 2])'))
        self.assertTrue(self.eval('bar2(null)'))

        self.assertFalse(self.eval('baz1($)', data=iter([1, 2])))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'baz1(null)')
        self.assertFalse(self.eval('baz2($)', data=iter([1, 2])))
        self.assertTrue(self.eval('baz2(null)'))
