# -*- coding: utf-8 -*-

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


class TestStrings(yaql.tests.TestCase):
    def test_scalar(self):
        self.assertEqual("some \ttext", self.eval("'some \\ttext'"))
        self.assertEqual(r"\\", self.eval(r"'\\\\'"))
        self.assertEqual("some \"text\"", self.eval(r'"some \"text\""'))

    def test_verbatim_strings(self):
        self.assertEqual('c:\\f\\x', self.eval(r"`c:\f\x`"))
        self.assertEqual('`', self.eval(r"`\``"))
        self.assertEqual('\\n', self.eval(r"`\n`"))
        self.assertEqual(r"\\", self.eval(r"`\\`"))

    def test_len(self):
        self.assertEqual(3, self.eval('len(abc)'))

    def test_to_upper(self):
        self.assertEqual('QQ', self.eval('qq.toUpper()'))
        self.assertEqual(u'ПРИВЕТ', self.eval(u'Привет.toUpper()'))

    def test_to_lower(self):
        self.assertEqual('qq', self.eval('QQ.toLower()'))
        self.assertEqual(u'привет', self.eval(u'Привет.toLower()'))

    def test_eq(self):
        self.assertTrue(self.eval('a = a'))
        self.assertFalse(self.eval('a = b'))

    def test_neq(self):
        self.assertFalse(self.eval('a != a'))
        self.assertTrue(self.eval('a != b'))

    def test_is_string(self):
        self.assertTrue(self.eval('isString(abc)'))
        self.assertFalse(self.eval('isString(null)'))
        self.assertFalse(self.eval('isString(123)'))
        self.assertFalse(self.eval('isString(true)'))

    def test_split(self):
        self.assertEqual(
            ['some', 'text'],
            self.eval("$.split('\\n')", data='some\ntext'))

    def test_rsplit(self):
        self.assertEqual(
            ['one\ntwo', 'three'],
            self.eval("$.rightSplit('\\n', 1)", data='one\ntwo\nthree'))

    def test_join(self):
        self.assertEqual('some-text', self.eval("[some, text].join('-')"))

    def test_join_pythonic(self):
        self.assertEqual('some-text', self.eval("'-'.join([some, text])"))

    def test_is_empty(self):
        self.assertTrue(self.eval("isEmpty('')"))
        self.assertTrue(self.eval("isEmpty(null)"))
        self.assertTrue(self.eval("null.isEmpty()"))
        self.assertTrue(self.eval("isEmpty('  ')"))
        self.assertFalse(self.eval("isEmpty('  x')"))

    def test_norm(self):
        self.assertIsNone(self.eval("norm('')"))
        self.assertIsNone(self.eval("norm(null)"))
        self.assertIsNone(self.eval("norm('  ')"))
        self.assertEqual('x', self.eval("norm('  x')"))

    def test_replace(self):
        self.assertEqual('AxxD', self.eval("ABBD.replace(B, x)"))
        self.assertEqual('AxxD', self.eval("ABxD.replace(B, x, 1)"))

    def test_replace_with_dict(self):
        self.assertEqual(
            'Az1D',
            self.eval('AxyD.replace({x => z, y => 1})'))

        self.assertEqual(
            'Ayfalse2D!', self.eval(
                "A122Dnull.replace({1 => y, 2 => false, null => '!'}, 1)"))

    def test_in(self):
        self.assertTrue(self.eval("B in ABC"))
        self.assertFalse(self.eval("D in ABC"))

    def test_str(self):
        self.assertEqual('null', self.eval('str(null)'))
        self.assertEqual('true', self.eval('str(true)'))
        self.assertEqual('false', self.eval('str(false)'))
        self.assertEqual('12', self.eval("str('12')"))

    def test_join_seq(self):
        self.assertEqual(
            'text-1-null-true',
            self.eval("[text, 1, null, true].select(str($)).join('-')"))

    def test_concat_plus(self):
        self.assertEqual('abc', self.eval("a +b + c"))

    def test_concat_func(self):
        self.assertEqual('abc', self.eval("concat(a, b, c)"))

    def test_format(self):
        self.assertEqual('a->b', self.eval("'{0}->{x}'.format(a, x => b)"))
        self.assertEqual('a->b', self.eval("format('{0}->{x}', a, x => b)"))

    def test_trim(self):
        self.assertEqual('x', self.eval("'  x  '.trim()"))
        self.assertEqual('x', self.eval("'abxba'.trim(ab)"))

    def test_trim_left(self):
        self.assertEqual('x  ', self.eval("'  x  '.trimLeft()"))
        self.assertEqual('xba', self.eval("'abxba'.trimLeft(ab)"))

    def test_trim_right(self):
        self.assertEqual('  x', self.eval("'  x  '.trimRight()"))
        self.assertEqual('abx', self.eval("'abxba'.trimRight(ab)"))

    def test_multiplication(self):
        self.assertEqual('xxx', self.eval("x * 3"))
        self.assertEqual('xxx', self.eval("3 * x"))

    def test_substring(self):
        data = 'abcdef'
        self.assertEqual('cdef', self.eval('$.substring(2)', data=data))
        self.assertEqual('ef', self.eval('$.substring(-2)', data=data))
        self.assertEqual('cde', self.eval('$.substring(2, 3)', data=data))
        self.assertEqual('de', self.eval('$.substring(-3, 2)', data=data))
        self.assertEqual('bcdef', self.eval('$.substring(1, -1)', data=data))
        self.assertEqual('bcdef', self.eval('$.substring(-5, -1)', data=data))

    def test_index_of(self):
        data = 'abcdefedcba'
        self.assertEqual(2, self.eval('$.indexOf(c)', data=data))
        self.assertEqual(2, self.eval('$.indexOf(c, 2)', data=data))
        self.assertEqual(-1, self.eval('$.indexOf(x)', data=data))
        self.assertEqual(5, self.eval('$.indexOf(f, 3)', data=data))
        self.assertEqual(7, self.eval('$.indexOf(dcb, -4, 3)', data=data))
        self.assertEqual(7, self.eval('$.indexOf(dcb, -4, 100)', data=data))
        self.assertEqual(-1, self.eval('$.indexOf(dcb, 0, 5)', data=data))

    def test_last_index_of(self):
        data = 'abcdefedcbabc'
        self.assertEqual(12, self.eval('$.lastIndexOf(c)', data=data))
        self.assertEqual(2, self.eval('$.lastIndexOf(c, 0, 4)', data=data))
        self.assertEqual(-1, self.eval('$.lastIndexOf(c, 3, 4)', data=data))
        self.assertEqual(12, self.eval('$.lastIndexOf(c, -1, 1)', data=data))

    def test_max(self):
        self.assertEqual('z', self.eval('max(a, z)'))

    def test_min(self):
        self.assertEqual('a', self.eval('min(a, z)'))

    def test_to_char_array(self):
        self.assertEqual(['a', 'b', 'c'], self.eval('abc.toCharArray()'))

    def test_characters(self):
        self.assertItemsEqual(
            ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
            self.eval('characters(octdigits => true, digits => true)'))

    def test_starts_with(self):
        self.assertTrue(self.eval("ABC.startsWith(A)"))
        self.assertTrue(self.eval("ABC.startsWith(B, A)"))
        self.assertFalse(self.eval("ABC.startsWith(C)"))
        self.assertRaises(
            exceptions.NoMatchingMethodException,
            self.eval, "ABC.startsWith(null)")

    def test_ends_with(self):
        self.assertTrue(self.eval("ABC.endsWith(C)"))
        self.assertTrue(self.eval("ABC.endsWith(B, C)"))
        self.assertFalse(self.eval("ABC.endsWith(B)"))
        self.assertRaises(
            exceptions.NoMatchingMethodException,
            self.eval, "ABC.endsWith(null)")

    def test_hex(self):
        self.assertEqual('0xff', self.eval('hex(255)'))
        self.assertEqual('-0x2a', self.eval('hex(-42)'))
