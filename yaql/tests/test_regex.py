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


class TestRegex(yaql.tests.TestCase):
    def test_matches(self):
        self.assertTrue(self.eval("regex('a.b').matches(axb)"))
        self.assertFalse(self.eval("regex('a.b').matches(abx)"))

    def test_matches_string_method(self):
        self.assertTrue(self.eval("axb.matches('a.b')"))
        self.assertFalse(self.eval("abx.matches('a.b')"))

    def test_matches_operator_regex(self):
        self.assertTrue(self.eval("axb =~ regex('a.b')"))
        self.assertFalse(self.eval("abx =~ regex('a.b')"))

    def test_not_matches_operator_regex(self):
        self.assertFalse(self.eval("axb !~ regex('a.b')"))
        self.assertTrue(self.eval("abx !~ regex('a.b')"))

    def test_matches_operator_string(self):
        self.assertTrue(self.eval("axb =~ 'a.b'"))
        self.assertFalse(self.eval("abx =~ 'a.b'"))

    def test_not_matches_operator_string(self):
        self.assertFalse(self.eval("axb !~ 'a.b'"))
        self.assertTrue(self.eval("abx !~ 'a.b'"))

    def test_search(self):
        self.assertEqual(
            '24.16',
            self.eval(r"regex(`(\d+)\.?(\d+)?`).search('a24.16b')"))

    def test_search_with_selector(self):
        self.assertEqual(
            '24.16 = 24(2-4) + 16(5-7)',
            self.eval(
                r"regex(`(\d+)\.?(\d+)?`).search("r"'aa24.16bb', "
                r"format('{0} = {1}({2}-{3}) + {4}({5}-{6})', "
                r"$.value, $2.value, $2.start, $2.end, "
                r"$3.value, $3.start, $3.end))"))

    def test_search_all(self):
        self.assertEqual(
            ['24', '16'],
            self.eval(r"regex(`\d+`).searchAll('a24.16b')"))

    def test_search_all_with_selector(self):
        self.assertEqual(
            ['24!', '16!'],
            self.eval(r"regex(`\d+`).searchAll('a24.16b', $.value+'!')"))

    def test_split(self):
        self.assertEqual(
            ['Words', 'words', 'words', ''],
            self.eval(r"regex(`\W+`).split('Words, words, words.')"))
        self.assertEqual(
            ['Words', ', ', 'words', ', ', 'words', '.', ''],
            self.eval(r"regex(`(\W+)`).split('Words, words, words.')"))
        self.assertEqual(
            ['Words', 'words, words.'],
            self.eval(r"regex(`\W+`).split('Words, words, words.', 1)"))
        self.assertEqual(
            ['0', '3', '9'],
            self.eval(r"regex('[a-f]+', ignoreCase => true).split('0a3B9')"))

    def test_split_on_string(self):
        self.assertEqual(
            ['Words', 'words', 'words', ''],
            self.eval(r"'Words, words, words.'.split(regex(`\W+`))"))
        self.assertEqual(
            ['Words', ', ', 'words', ', ', 'words', '.', ''],
            self.eval(r"'Words, words, words.'.split(regex(`(\W+)`))"))
        self.assertEqual(
            ['Words', 'words, words.'],
            self.eval(r"'Words, words, words.'.split(regex(`\W+`), 1)"))
        self.assertEqual(
            ['0', '3', '9'],
            self.eval(r"'0a3B9'.split(regex('[a-f]+', ignoreCase => true))"))

    def test_replace(self):
        self.assertEqual(
            'axxbxx',
            self.eval(r"regex(`\d+`).replace(a12b23, xx)"))
        self.assertEqual(
            'axxb23',
            self.eval(r"regex(`\d+`).replace(a12b23, xx, 1)"))

    def test_replace_backref(self):
        self.assertEqual(
            'Foo_Bar_Foo',
            self.eval(r"regex(`([a-z0-9])([A-Z])`).replace("
                      "FooBarFoo, `\\1_\\2`)"))

    def test_replace_on_string(self):
        self.assertEqual(
            'axxbxx',
            self.eval(r"a12b23.replace(regex(`\d+`), xx)"))
        self.assertEqual(
            'axxb23',
            self.eval(r"a12b23.replace(regex(`\d+`), xx, 1)"))

    def test_replace_by(self):
        self.assertEqual(
            'axxbyy',
            self.eval(r"regex(`\d+`).replaceBy(a12b23, "
                      r"let(a => int($.value)) -> switch("
                      r"$a < 20 => xx, true => yy))"))

        self.assertEqual(
            'axxb23',
            self.eval(r"regex(`\d+`).replaceBy(a12b23, "
                      r"let(a => int($.value)) -> switch("
                      r"$a < 20 => xx, true => yy), 1)"))

    def test_replace_by_on_string(self):
        self.assertEqual(
            'axxbyy',
            self.eval(r"a12b23.replaceBy(regex(`\d+`), "
                      r"with(int($.value)) -> switch("
                      r"$ < 20 => xx, true => yy))"))

        self.assertEqual(
            'axxb23',
            self.eval(r"a12b23.replaceBy(regex(`\d+`), "
                      r"let(a => int($.value)) -> switch("
                      r"$a < 20 => xx, true => yy), 1)"))

    def test_escape_regex(self):
        self.assertEqual(
            '\\[',
            self.eval(r"escapeRegex('[')"))

    def test_is_regex(self):
        self.assertTrue(self.eval('isRegex(regex("a.b"))'))
        self.assertFalse(self.eval('isRegex(123)'))
        self.assertFalse(self.eval('isRegex(abc)'))
