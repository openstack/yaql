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

    def test_lambda_passing(self):
        delegate = lambda x: x ** 2
        self.assertEqual(
            9,
            self.eval('$(3)', data=delegate))

    def test_calling_non_callable(self):
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, '$(a)', data={'a': 9})

    def test_function_passing(self):
        def func(x, y, z):
            return (x - y) * z

        context = self.context
        context['func'] = func
        self.assertEqual(
            8,
            self.eval('$func(5, z => 2, y => 1)', data=func))

    def test_lambda_expression(self):
        delegate = lambda x: x ** 2
        self.assertEqual(
            9,
            self.eval('$.x[0](3)', data={'x': [delegate]}))

        self.assertEqual(
            9,
            self.eval('($.x[0])(3)', data={'x': [delegate]}))

    def test_2nd_order_lambda(self):
        delegate = lambda y: lambda x: x ** y
        self.assertEqual(
            16,
            self.eval('$(2)(4)', data=delegate))

    def test_2nd_order_lambda_expression(self):
        delegate = lambda y: {'key': lambda x: x ** y}
        self.assertEqual(
            16,
            self.eval('$(2)[key](4)', data=delegate))

    def test_2nd_order_lambda_collection_expression(self):
        delegate = lambda y: lambda x: y ** x
        self.assertEqual(
            [1, 8, 27],
            self.eval(
                'let(func => $) -> [1, 2, 3].select($func($)).select($(3))',
                data=delegate))

    def test_lambda_func(self):
        self.assertEqual(
            [2, 4, 6],
            self.eval('let(func => lambda(2 * $)) -> $.select($func($))',
                      data=[1, 2, 3]))

    def test_lambda_func_2nd_order(self):
        self.assertEqual(
            5,
            self.eval('lambda(let(outer => $) -> lambda($outer - $))(7)(2)'))

    def test_lambda_closure(self):
        data = [1, 2, 3, 4, 5, 6]
        self.assertEqual([3, 4, 5, 6], self.eval(
            '$.where(lambda($ > 3)($+1))',
            data=data))

        # lambda can access value from "where"'s context
        # so we can omit parameter
        self.assertEqual([4, 5, 6], self.eval(
            '$.where(lambda($ > 3)())',
            data=data))

    def test_properties(self):
        @specs.yaql_property(int)
        def neg_value(value):
            return -value

        self.context.register_function(neg_value)
        self.assertEqual(-123, self.eval('123.negValue'))
        self.assertRaises(exceptions.NoMatchingFunctionException,
                          self.eval, '"123".negValue')
        self.assertRaises(exceptions.NoMatchingFunctionException,
                          self.eval, 'null.negValue')
        self.assertRaises(exceptions.NoFunctionRegisteredException,
                          self.eval, '123.neg_value')

    def test_call_function(self):
        self.assertEqual(
            2,
            self.eval('call(len, [[1,2]], {})'))
        self.assertEqual(
            2,
            self.eval('call(len, [], {"sequence" => [1,2]})'))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'call(len, [[1,2]], null)')
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'call(len, null, {sequence => [1,2]})')
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'call(len, [], {invalid => [1,2]})')
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'call(len, [1, 2], {})')
        self.assertTrue(self.eval('call(isEmpty, [null], {})'))

    def test_call_method(self):
        self.assertEqual(
            2,
            self.eval('call(len, [], {}, [1,2])'))
        self.assertRaises(
            exceptions.NoMatchingMethodException,
            self.eval, 'call(len, [[1,2]], {}, [1,2])')
        self.assertRaises(
            exceptions.NoMatchingMethodException,
            self.eval, 'call(len, [], {sequence => [1,2]}, [1, 2])')
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'call(len, [], null, [1, 2])')
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'call(len, null, {sequence => [1,2]}, [1, 2])')
        self.assertTrue(self.eval('call(isEmpty, [], {}, null)'))
