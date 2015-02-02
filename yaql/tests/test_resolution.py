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


class TestResolution(yaql.tests.TestCase):
    def test_resolve_parameter_count_single_layer(self):
        def f1(a):
            return a

        def f2(a, b):
            return a + b

        self.context.register_function(f1, name='f')
        self.context.register_function(f2, name='f')

        self.assertEqual(12, self.eval('f(12)'))
        self.assertEqual(25, self.eval('f(12, 13)'))

    def test_resolve_parameter_count_multi_layer(self):
        def f1(a):
            return a

        def f2(a, b):
            return a + b

        context1 = self.context.create_child_context()
        context1.register_function(f1, name='f')
        context2 = context1.create_child_context()
        context2.register_function(f2, name='f')

        self.assertEqual(12, self.eval('f(12)', context=context2))
        self.assertEqual(25, self.eval('f(12, 13)', context=context2))

    def test_layer_override(self):
        def f1(a):
            return a

        def f2(a):
            return -a

        context1 = self.context.create_child_context()
        context1.register_function(f1, name='f')
        context2 = context1.create_child_context()
        context2.register_function(f2, name='f')

        self.assertEqual(-12, self.eval('f(12)', context=context2))

    def test_single_layer_ambiguity(self):
        def f1(a):
            return a

        def f2(a):
            return -a

        context1 = self.context.create_child_context()
        context1.register_function(f1, name='f')
        context1.register_function(f2, name='f')

        self.assertRaises(
            exceptions.AmbiguousFunctionException,
            self.eval, 'f(12)', context=context1)

    def test_single_layer_laziness_ambiguity(self):
        @specs.parameter('a', yaqltypes.Lambda())
        def f1(a):
            return a()

        def f2(a):
            return -a

        def f3(a, b):
            return a + b

        context1 = self.context.create_child_context()
        context1.register_function(f1, name='f')
        context1.register_function(f2, name='f')
        context1.register_function(f3, name='f')

        self.assertRaises(
            exceptions.AmbiguousFunctionException,
            self.eval, 'f(2 * $)', data=3, context=context1)

        self.assertEqual(25, self.eval('f(12, 13)', context=context1))

    def test_multi_layer_laziness_ambiguity(self):
        @specs.parameter('a', yaqltypes.Lambda())
        def f1(a, b):
            return a() + b

        @specs.parameter('a', yaqltypes.Lambda())
        def f2(a, b):
            return a() + b

        @specs.parameter('b', yaqltypes.Lambda())
        def f3(a, b):
            return -a - b()

        @specs.parameter('a', yaqltypes.Lambda())
        def f4(a, b):
            return -a() + b

        context1 = self.context.create_child_context()
        context1.register_function(f1, name='foo')
        context1.register_function(f2, name='bar')
        context2 = context1.create_child_context()
        context2.register_function(f3, name='foo')
        context2.register_function(f4, name='bar')

        self.assertRaises(
            exceptions.AmbiguousFunctionException,
            self.eval, 'foo(12, 13)', context=context2)

        self.assertEqual(
            1,
            self.eval('bar(12, 13)', context=context2))

    def test_ambiguous_method(self):
        self.context.register_function(
            lambda c, s: 1, name='select', method=True)
        self.assertRaises(
            exceptions.AmbiguousMethodException,
            self.eval, '[1,2].select($)')
