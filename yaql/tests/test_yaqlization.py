#    Copyright (c) 2016 Mirantis, Inc.
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

import re

from yaql.language import exceptions
from yaql import tests
from yaql import yaqlization


class TestYaqlization(tests.TestCase):
    def _get_sample_class(self):
        class D(object):
            d_attr = 777

        class C(object):
            def __init__(self):
                self.attr = 123

            def m_foo(self, arg1, arg2):
                return arg1 - arg2

            def bar(self, string):
                return string.upper()

            def get_d(self):
                return D()

            @staticmethod
            def static(string):
                return string.upper()

            @classmethod
            def clsmethod(cls, string):
                return string.upper()

            @property
            def prop(self):
                return self.attr

            def __getitem__(self, item):
                return item

        return C

    def test_method_call_yaqlized_object(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj)

        self.assertEqual(3, self.eval('$.m_foo(5, 2)', obj))
        self.assertEqual(3, self.eval('$.m_foo(5, arg2 => 2)', obj))
        self.assertEqual(3, self.eval('$.m_foo(arg2 => 2, arg1 => 6-1)', obj))
        self.assertEqual('A', self.eval('$.bar(a)', obj))
        self.assertEqual('B', self.eval('$.static(b)', obj))
        self.assertEqual('C', self.eval('$.clsmethod(c)', obj))
        self.assertRaises(
            exceptions.NoFunctionRegisteredException,
            self.eval, 'm_foo($, 5, 2)', obj)
        self.assertEqual(3, self.eval('$?.m_foo(5, 2)', obj))
        self.assertIsNone(self.eval('$?.m_foo(5, 2)', None))

    def test_method_call_yaqlized_class(self):
        cls = self._get_sample_class()
        yaqlization.yaqlize(cls)
        obj = cls()
        self.assertEqual(3, self.eval('$.m_foo(5, 2)', obj))

    def test_method_call_not_yaqlized(self):
        obj = self._get_sample_class()()
        self.assertRaises(
            exceptions.NoMethodRegisteredException,
            self.eval, '$.m_foo(5, 2)', obj)

    def test_method_call_forbidden(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj, yaqlize_methods=False)
        self.assertRaises(
            exceptions.NoMethodRegisteredException,
            self.eval, '$.m_foo(5, 2)', obj)

    def test_property_access(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj)

        self.assertEqual(123, self.eval('$.attr', obj))
        self.assertEqual(123, self.eval('$.prop', obj))
        self.assertEqual(123, self.eval('$?.prop', obj))
        self.assertIsNone(self.eval('$?.prop', None))
        self.assertRaises(AttributeError, self.eval, '$.invalid', obj)

    def test_indexation(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj)

        self.assertEqual('key', self.eval('$[key]', obj))

    def test_method_call_whitelist_string(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj, whitelist=['m_foo'])

        self.assertEqual(3, self.eval('$.m_foo(5, 2)', obj))
        self.assertRaises(AttributeError, self.eval, '$.bar(a)', obj)

    def test_method_call_whitelist_regexp(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj, whitelist=[re.compile('^m_*')])

        self.assertEqual(3, self.eval('$.m_foo(5, 2)', obj))
        self.assertRaises(AttributeError, self.eval, '$.bar(a)', obj)

    def test_method_call_whitelist_callable(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj, whitelist=[lambda t: t.startswith('m_')])

        self.assertEqual(3, self.eval('$.m_foo(5, 2)', obj))
        self.assertRaises(AttributeError, self.eval, '$.bar(a)', obj)

    def test_method_call_blacklist_string(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj, blacklist=['m_foo'])

        self.assertRaises(AttributeError, self.eval, '$.m_foo(5, 2)', obj)
        self.assertEqual('A', self.eval('$.bar(a)', obj))

    def test_method_call_blacklist_regexp(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj, blacklist=[re.compile('^m_*')])

        self.assertRaises(AttributeError, self.eval, '$.m_foo(5, 2)', obj)
        self.assertEqual('A', self.eval('$.bar(a)', obj))

    def test_method_call_blacklist_callable(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj, blacklist=[lambda t: t.startswith('m_')])

        self.assertRaises(AttributeError, self.eval, '$.m_foo(5, 2)', obj)
        self.assertEqual('A', self.eval('$.bar(a)', obj))

    def test_property_access_blacklist(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj, blacklist=['prop'])

        self.assertEqual(123, self.eval('$.attr', obj))
        self.assertRaises(AttributeError, self.eval, '$.prop', obj)

    def test_indexation_blacklist(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj, blacklist=[lambda t: t.startswith('_')])

        self.assertEqual('key', self.eval('$[key]', obj))
        self.assertRaises(KeyError, self.eval, '$[_key]', obj)

    def test_auto_yaqlization(self):
        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj)

        self.assertRaises(
            exceptions.NoFunctionRegisteredException,
            self.eval, '$.get_d().d_attr', obj)

        obj = self._get_sample_class()()
        yaqlization.yaqlize(obj, auto_yaqlize_result=True)

        self.assertEqual(777, self.eval('$.get_d().d_attr', obj))

    def test_yaqlify_decorator(self):
        @yaqlization.yaqlize
        class C(object):
            attr = 555

        self.assertEqual(555, self.eval('$.attr', C()))

    def test_yaqlify_decorator_with_parameters(self):
        @yaqlization.yaqlize(yaqlize_attributes=True)
        class C(object):
            attr = 555

        self.assertEqual(555, self.eval('$.attr', C()))
