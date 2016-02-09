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


class TestMath(yaql.tests.TestCase):
    def test_binary_plus_int(self):
        res = self.eval('2 + 3')
        self.assertEqual(5, res)
        self.assertIsInstance(res, int)

    def test_binary_plus_float(self):
        res = self.eval('2 + 3.0')
        self.assertEqual(5, res)
        self.assertIsInstance(res, float)

        res = self.eval('2.3+3.5')
        self.assertEqual(5.8, res)
        self.assertIsInstance(res, float)

    def test_binary_minus_int(self):
        res = self.eval('12 -3')
        self.assertEqual(9, res)
        self.assertIsInstance(res, int)

    def test_binary_minus_float(self):
        res = self.eval('1 - 2.1')
        self.assertEqual(-1.1, res)
        self.assertIsInstance(res, float)

        res = self.eval('123.321- 0.321')
        self.assertEqual(123.0, res)
        self.assertIsInstance(res, float)

    def test_multiplication_int(self):
        res = self.eval('3 * 2')
        self.assertEqual(6, res)
        self.assertIsInstance(res, int)
        self.assertEqual(-6, self.eval('3 * -2'))
        self.assertEqual(6, self.eval('-3 * -2'))

    def test_multiplication_float(self):
        res = self.eval('3.0 * 2.0')
        self.assertEqual(6.0, res)
        self.assertIsInstance(res, float)
        self.assertAlmostEqual(-6.51, self.eval('3.1 * -2.1'))
        self.assertAlmostEqual(6.51, self.eval('-3.1 * -2.1'))

    def test_division(self):
        self.assertEqual(3, self.eval('7 / 2'))
        self.assertEqual(-4, self.eval('7 / -2'))
        self.assertAlmostEqual(2.5, self.eval('5 / 2.0'))
        self.assertAlmostEqual(2.5, self.eval('5.0 / 2'))
        self.assertAlmostEqual(-2.5, self.eval('-5.0 / 2.0'))
        self.assertRaises(ZeroDivisionError, self.eval, '7 / 0')
        self.assertRaises(ZeroDivisionError, self.eval, '7 / -0.0')

    def test_brackets(self):
        self.assertEqual(-4, self.eval('1 - (2) - 3'))
        self.assertEqual(2, self.eval('1 - (2 - 3)'))

    def test_unary_minus(self):
        self.assertEqual(-4, self.eval('-4'))
        self.assertEqual(-12.0, self.eval('-12.0'))
        self.assertEqual(4, self.eval('3--1'))
        self.assertEqual(2, self.eval('3+-1'))
        self.assertAlmostEqual(4.3, self.eval('3.2 - -1.1'))
        self.assertEqual(2, self.eval('-(1-3)'))

    def test_unary_plus(self):
        self.assertEqual(4, self.eval('+4'))
        self.assertEqual(12.0, self.eval('+12.0'))
        self.assertEqual(2, self.eval('3-+1'))
        self.assertEqual(4, self.eval('3++1'))
        self.assertAlmostEqual(2.1, self.eval('3.2 - +1.1'))

    def test_modulo_int(self):
        res = self.eval('9 mod 5')
        self.assertEqual(4, res)
        self.assertIsInstance(res, int)
        self.assertEqual(-1, self.eval('9 mod -5'))

    def test_modulo_float(self):
        res = self.eval('9.0 mod 5')
        self.assertEqual(4.0, res)
        self.assertIsInstance(res, float)

        res = self.eval('9 mod 5.0')
        self.assertEqual(4.0, res)
        self.assertIsInstance(res, float)

        res = self.eval('9.0 mod 5.0')
        self.assertEqual(4.0, res)
        self.assertIsInstance(res, float)

        self.assertAlmostEqual(-1.1, self.eval('9.1 mod -5.1'))

    def test_abs(self):
        self.assertEqual(4, self.eval('abs(-4)'))
        self.assertEqual(4, self.eval('abs(4)'))
        self.assertEqual(4.4, self.eval('abs(-4.4)'))

    def test_gt(self):
        res = self.eval('5 > 3')
        self.assertIsInstance(res, bool)
        self.assertTrue(res)
        self.assertFalse(self.eval('3 > 3'))

    def test_lt(self):
        res = self.eval('3 < 5')
        self.assertIsInstance(res, bool)
        self.assertTrue(res)
        self.assertFalse(self.eval('3 < 3'))
        self.assertTrue(self.eval('2.5 < 3'))

    def test_gte(self):
        res = self.eval('5 >= 3')
        self.assertIsInstance(res, bool)
        self.assertTrue(res)
        self.assertTrue(self.eval('3 >= 3'))
        self.assertTrue(self.eval('3.5 > 3'))
        self.assertFalse(self.eval('2 >= 3'))

    def test_lte(self):
        res = self.eval('3 <= 5')
        self.assertIsInstance(res, bool)
        self.assertTrue(res)
        self.assertTrue(self.eval('3 <= 3'))
        self.assertFalse(self.eval('3 <= 2'))

    def test_eq(self):
        self.assertTrue(self.eval('5 = 5'))
        self.assertTrue(self.eval('1.0 = 1'))
        self.assertFalse(self.eval('5 = 6'))

    def test_neq(self):
        self.assertFalse(self.eval('5 != 5'))
        self.assertFalse(self.eval('0 != 0.0'))
        self.assertTrue(self.eval('5 != 6'))

    def test_zero_division(self):
        self.assertRaises(ZeroDivisionError, self.eval, '0/0')

    def test_random(self):
        self.assertTrue(self.eval('with(random()) -> $ >= 0 and $ < 1'))
        self.assertTrue(self.eval('with(random(2, 5)) -> $ >= 2 and $ <= 5'))

    def test_int(self):
        self.assertEqual(5, self.eval("int('5')"))
        self.assertEqual(5, self.eval('int(5.2)'))
        self.assertEqual(0, self.eval('int(null)'))

    def test_float(self):
        self.assertAlmostEqual(-1.23, self.eval("float('-1.23')"))
        self.assertEqual(0.0, self.eval('float(null)'))

    def test_bitwise_or(self):
        self.assertEqual(3, self.eval('bitwiseOr(1, 3)'))
        self.assertEqual(3, self.eval('bitwiseOr(1, 2)'))

    def test_bitwise_and(self):
        self.assertEqual(1, self.eval('bitwiseAnd(1, 3)'))
        self.assertEqual(0, self.eval('bitwiseAnd(1, 2)'))

    def test_bitwise_xor(self):
        self.assertEqual(2, self.eval('bitwiseXor(1, 3)'))
        self.assertEqual(3, self.eval('bitwiseXor(1, 2)'))

    def test_bitwise_not(self):
        self.assertEqual(-2, self.eval('bitwiseNot(1)'))

    def test_shift_bits_left(self):
        self.assertEqual(32, self.eval('shiftBitsLeft(1, 5)'))

    def test_shift_bits_right(self):
        self.assertEqual(2, self.eval('shiftBitsRight(32, 4)'))
        self.assertEqual(0, self.eval('shiftBitsRight(32, 6)'))

    def test_pow(self):
        self.assertEqual(32, self.eval('pow(2, 5)'))
        self.assertEqual(4, self.eval('pow(2, 5, 7)'))

    def test_sign(self):
        self.assertEqual(1, self.eval('sign(123)'))
        self.assertEqual(-1, self.eval('sign(-123)'))
        self.assertEqual(0, self.eval('sign(0)'))

    def test_round(self):
        self.assertAlmostEqual(2.0, self.eval('round(2.3)'))
        self.assertAlmostEqual(2.3, self.eval('round(2.345, 1)'))

    def test_is_integer(self):
        self.assertTrue(self.eval('isInteger(-2)'))
        self.assertTrue(self.eval('isInteger(2)'))
        self.assertFalse(self.eval('isInteger(2.3)'))
        self.assertFalse(self.eval('isInteger(abc)'))
        self.assertFalse(self.eval('isInteger(true)'))

    def test_is_number(self):
        self.assertTrue(self.eval('isNumber(-2)'))
        self.assertTrue(self.eval('isNumber(2)'))
        self.assertTrue(self.eval('isNumber(2.3)'))
        self.assertFalse(self.eval('isNumber(abc)'))
        self.assertFalse(self.eval('isNumber(true)'))
