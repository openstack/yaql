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

import testtools
from testtools import matchers

from yaql.language import contexts
from yaql.language import specs


class TestContexts(testtools.TestCase):
    def test_store_data(self):
        context = contexts.Context()
        context['key'] = 123
        self.assertEqual(123, context['key'])

    def test_name_normalization(self):
        context = contexts.Context()
        context['key'] = 123
        self.assertEqual(123, context['$key'])

    def test_empty_name(self):
        context = contexts.Context()
        context[''] = 123
        self.assertEqual(123, context['$'])
        self.assertEqual(123, context[''])
        self.assertEqual(123, context['$1'])

    def test_missing_key_access(self):
        context = contexts.Context()
        self.assertIsNone(context['key'])

    def test_key_deletion(self):
        context = contexts.Context()
        context['key'] = 123
        del context['key']
        self.assertIsNone(context['key'])

    def test_child_contexts(self):
        context = contexts.Context()
        context2 = context.create_child_context()
        context['key'] = 123
        self.assertEqual(123, context2['key'])
        context2['key'] = 345
        self.assertEqual(345, context2['key'])
        del context2['key']
        self.assertEqual(123, context2['key'])

    def test_get_functions(self):
        def f():
            pass

        def f_():
            pass

        def f__():
            pass

        def g():
            pass

        context = contexts.Context()
        context2 = context.create_child_context()

        context.register_function(f)
        context.register_function(f_)
        context.register_function(g, exclusive=True)
        context2.register_function(f__)

        functions, is_exclusive = context.get_functions('f')
        self.assertFalse(is_exclusive)
        self.assertIsInstance(functions, set)
        self.assertThat(functions, testtools.matchers.HasLength(2))
        self.assertThat(
            functions, matchers.AllMatch(matchers.IsInstance(
                specs.FunctionDefinition)))
        functions, is_exclusive = context2.get_functions('g')
        self.assertFalse(is_exclusive)
        functions, is_exclusive = context2.get_functions('f')
        self.assertFalse(is_exclusive)
        self.assertThat(functions, testtools.matchers.HasLength(1))

    def test_collect_functions(self):
        def f():
            pass

        def f_():
            pass

        def f__():
            pass

        context = contexts.Context()
        context2 = context.create_child_context()
        context3 = context2.create_child_context()
        context.register_function(f)
        context.register_function(f_)
        context3.register_function(f__)
        functions = context3.collect_functions('f')
        self.assertThat(functions, testtools.matchers.HasLength(2))
        self.assertThat(functions[0], testtools.matchers.HasLength(1))
        self.assertThat(functions[1], testtools.matchers.HasLength(2))

    def test_function_in(self):
        def f():
            pass

        def f_():
            pass

        def f__():
            pass

        context = contexts.Context()
        context2 = context.create_child_context()
        context3 = context2.create_child_context()
        context.register_function(f)
        context.register_function(f_)
        context3.register_function(f__)
        functions = context3.collect_functions('f')
        self.assertNotIn(specs.get_function_definition(f__), context3)
        self.assertIn(functions[0].pop(), context3)
        self.assertNotIn(functions[1].pop(), context3)

    def test_data(self):
        context = contexts.Context()
        context2 = context.create_child_context()
        context['key'] = 123
        context2['key2'] = 321
        self.assertIn('key', context)
        self.assertIn('key2', context2)
        self.assertIn('$key', context)
        self.assertNotIn('key2', context)
        self.assertNotIn('key', context2)

    def test_keys(self):
        context = contexts.Context()
        context2 = context.create_child_context()
        context['key'] = 123
        context2['key2'] = 321
        keys = list(context2.keys())
        self.assertThat(keys, testtools.matchers.HasLength(1))
        self.assertEqual(keys[0], '$key2')

    def test_delete_function(self):
        def f():
            pass

        def f_():
            pass

        context = contexts.Context()
        context.register_function(f)
        context2 = context.create_child_context()
        context2.register_function(f_)

        functions, is_exclusive = context2.get_functions('f')
        spec = functions.pop()
        self.assertIn(spec, context2)
        context2.delete_function(spec)
        self.assertNotIn(spec, context2)
        functions, is_exclusive = context.get_functions('f')
        self.assertThat(functions, matchers.HasLength(1))

    @staticmethod
    def create_multi_context():
        def f():
            pass

        def f_():
            pass

        def f__():
            pass

        def f___():
            pass

        context = contexts.Context()
        context2 = context.create_child_context()
        context3 = context2.create_child_context()
        context4 = contexts.Context()
        context5 = context4.create_child_context()
        mc = contexts.MultiContext([context3, context5])
        context.register_function(f)
        context2.register_function(f___)
        context4.register_function(f_)
        context5.register_function(f__)
        context3['key'] = 'context3'
        context5['key'] = 'context5'
        context4['key2'] = 'context4'
        context['key3'] = 'context1'
        mc['key4'] = 'mc'
        return mc

    def test_multi_context_data(self):
        mc = self.create_multi_context()
        self.assertEqual(mc['key'], 'context3')
        self.assertEqual(mc['key2'], 'context4')
        self.assertEqual(mc['key3'], 'context1')

    def test_multi_context_data_in(self):
        mc = self.create_multi_context()
        self.assertIn('key', mc)
        self.assertIn('key4', mc)
        self.assertNotIn('key2', mc)
        self.assertIn('key2', mc.parent)
        self.assertNotIn('key3', mc.parent)
        self.assertNotIn('key4', mc.parent)
        self.assertIn('key3', mc.parent.parent)
        self.assertIsNone(mc.parent.parent.parent)

    def test_multi_context_keys(self):
        mc = self.create_multi_context()
        self.assertCountEqual(['$key4', '$key'], mc.keys())
        self.assertCountEqual(['$key2'], mc.parent.keys())
        self.assertCountEqual(['$key3'], mc.parent.parent.keys())

    def test_multi_context_get_functions(self):
        def f():
            pass

        mc = self.create_multi_context()
        mc.register_function(f)
        functions, is_exclusive = mc.get_functions('f')
        self.assertFalse(is_exclusive)
        self.assertThat(functions, matchers.HasLength(2))
        functions, is_exclusive = mc.parent.get_functions('f')
        self.assertFalse(is_exclusive)
        self.assertThat(functions, matchers.HasLength(2))
        functions, is_exclusive = mc.parent.parent.get_functions('f')
        self.assertFalse(is_exclusive)
        self.assertThat(functions, matchers.HasLength(1))

    def test_multi_context_collect_functions(self):
        def f():
            pass

        mc = self.create_multi_context()
        mc.register_function(f)
        levels = mc.collect_functions('f')
        self.assertThat(levels, matchers.HasLength(3))
        self.assertThat(levels[0], matchers.HasLength(2))
        self.assertThat(levels[1], matchers.HasLength(2))
        self.assertThat(levels[2], matchers.HasLength(1))

    def test_multi_context_function_in(self):
        mc = self.create_multi_context()
        functions, is_exclusive = mc.get_functions('f')
        for fd in functions:
            self.assertIn(fd, mc)

    def test_multi_context_delete_data(self):
        mc = self.create_multi_context()
        del mc['key']
        self.assertNotIn('key', mc)

    def test_multi_context_function_delete(self):
        mc = self.create_multi_context()
        functions, is_exclusive = mc.get_functions('f')
        for fd in functions:
            mc.delete_function(fd)
        functions, is_exclusive = mc.get_functions('f')
        self.assertThat(functions, matchers.HasLength(0))

    @staticmethod
    def create_linked_context():
        def f():
            pass

        def g():
            pass

        def g_():
            pass

        def g__():
            pass

        context1 = contexts.Context()
        context2 = contexts.Context()
        context1.register_function(f)
        context1.register_function(g)
        context2.register_function(g_)
        context1['key'] = 'context1'
        context1['key1'] = 'context1'
        context2['key'] = 'context2'
        context2['key2'] = 'context2'

        context3 = context2.create_child_context()
        context3.register_function(g__)
        context3['key'] = 'context3'
        context2['key3'] = 'context3'

        return contexts.LinkedContext(
            parent_context=context1, linked_context=context3)

    def test_linked_context_data(self):
        mc = self.create_linked_context()
        self.assertEqual(mc['key'], 'context3')
        self.assertEqual(mc['key2'], 'context2')
        self.assertEqual(mc['key3'], 'context3')
        self.assertEqual(mc['key3'], 'context3')
        self.assertEqual(mc.parent['key'], 'context2')
        self.assertEqual(mc.parent.parent['key'], 'context1')

    def test_linked_context_collect_functions(self):
        mc = self.create_linked_context()
        self.assertThat(mc.collect_functions('f'), matchers.HasLength(1))
        levels = mc.collect_functions('g')
        self.assertThat(levels, matchers.HasLength(3))
        self.assertThat(levels[0], matchers.HasLength(1))
        self.assertThat(levels[1], matchers.HasLength(1))
        self.assertThat(levels[2], matchers.HasLength(1))

    def test_linked_context_delete_data(self):
        mc = self.create_linked_context()
        self.assertIn('key', mc)
        del mc['key']
        self.assertNotIn('key', mc)

    def test_linked_context_function_in(self):
        mc = self.create_linked_context()
        functions, is_exclusive = mc.get_functions('f')
        for fd in functions:
            self.assertIn(fd, mc)
