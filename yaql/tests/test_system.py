#    Copyright (c) 2014 Mirantis, Inc.
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
import types

import unittest
from yaql.tests import YaqlTest
import yaql
from yaql.language.engine import parameter


class TestSystem(YaqlTest):

    def test_string_concat(self):
        self.assertEquals("abcqwe", self.eval('abc + qwe'))
        self.assertEquals("abc qwe", self.eval("abc + ' ' + qwe"))

    def test_get_context_data(self):
        obj = object()
        self.assertEquals(obj, self.eval('$', obj))

    def test_get_object_attribution(self):
        class Foo(object):
            def __init__(self, value):
                self.bar = value

        foo = Foo(42)
        self.assertEquals(42, self.eval('$.bar', foo))
        bar = Foo(foo)
        self.assertEquals(42, self.eval('$.bar.bar', bar))

    def test_missing_object_property_attribution(self):
        class Foo(object):
            def __init__(self, value):
                self.bar = value

        foo = Foo(42)
        self.assertRaises(Exception, self.eval, '$.foo.missing', foo)
        self.assertRaises(Exception, self.eval, '$.foo.missing',
                          {'foo': 'bar'})

    def test_int_bool_resolving(self):
        @parameter('param', arg_type=types.IntType)
        def int_func(param):
            return "int: " + str(param)

        @parameter('param', arg_type=types.BooleanType)
        def bool_func(param):
            return "bool: " + str(param)

        context1 = yaql.create_context(False)
        context2 = yaql.create_context(False)
        context3 = yaql.create_context(False)
        context4 = yaql.create_context(False)

        context1.register_function(int_func, 'foo')
        context2.register_function(bool_func, 'foo')
        context3.register_function(int_func, 'foo')
        context3.register_function(bool_func, 'foo')
        context4.register_function(bool_func, 'foo')
        context4.register_function(int_func, 'foo')

        self.assertEquals("int: 1", self.eval('foo(1)', context=context1))
        self.assertEquals("int: 0", self.eval('foo(0)', context=context1))
        self.assertRaises(Exception, self.eval, "foo('1')", context=context1)
        self.assertRaises(Exception, self.eval, 'foo(1)', context=context2)

        self.assertEquals("bool: True",
                          self.eval('foo(true)', context=context2))
        self.assertEquals("bool: False",
                          self.eval('foo(false)', context=context2))
        self.assertRaises(Exception, self.eval, "foo(1)", context=context2)
        self.assertRaises(Exception, self.eval, 'foo(0)', context=context2)
        self.assertRaises(Exception, self.eval, 'foo(True)', context=context2)
        self.assertRaises(Exception, self.eval, "foo('true')",
                          context=context2)

        self.assertEquals("int: 1", self.eval('foo(1)', context=context3))
        self.assertEquals("int: 0", self.eval('foo(0)', context=context3))
        self.assertEquals("bool: True",
                          self.eval('foo(true)', context=context3))
        self.assertEquals("bool: False",
                          self.eval('foo(false)', context=context3))

        self.assertEquals("int: 1", self.eval('foo(1)', context=context4))
        self.assertEquals("int: 0", self.eval('foo(0)', context=context4))
        self.assertEquals("bool: True",
                          self.eval('foo(true)', context=context4))
        self.assertEquals("bool: False",
                          self.eval('foo(false)', context=context4))

    def test_get_dict_attribution(self):
        d = {
            'key1': 'string1',
            'key2': {
                'inner': {
                    'last': 42,
                    'lastString': 'string'
                }
            },
            'composite key': 3
        }
        self.assertEquals('string1', self.eval('$.key1', d))
        self.assertEquals('string', self.eval('$.key2.inner.lastString', d))
        self.assertEquals(42, self.eval('$.key2.inner.last', d))
        self.assertEquals(3, self.eval("$.'composite key'", d))

    def test_missing_key_dict_attributions(self):
        d = {
            'key1': 'string1',
            'key2': {
                'inner': {
                    'last': 42,
                    'lastString': 'string'
                }
            },
            'composite key': 3
        }
        self.assertEquals(None, self.eval("$.'missing key'", d))
        self.assertEquals(None, self.eval("$.key2.missing", d))

    def test_function_call(self):
        def foo():
            return 42

        self.context.register_function(foo, 'test')
        self.assertEquals(42, self.eval("test()"))

    def test_composite_function_call_1(self):
        def foo():
            return 42

        self.context.register_function(foo, 'long.namespace.based.name')
        self.assertEval(42, "'long.namespace.based.name'()")

    def test_composite_function_call_2(self):
        def foo():
            return 42

        self.context.register_function(foo, 'some spaced name\'s')
        self.assertEval(42, "'some spaced name\\'s'()")

    def test_return_same_function(self):
        def foo(bar):
            return bar

        self.context.register_function(foo, 'foo')
        self.assertEquals('bar', self.eval('foo(bar)'))

    def test_return_same_method(self):
        def foo(self):
            return self

        self.context.register_function(foo, 'foo')
        self.assertEquals('bar', self.eval('bar.foo()'))

    def test_self_reordering(self):
        def concat_right(self, arg):
            return self + ',' + arg

        @parameter('self', is_self=True)
        def concat_left(arg, self):
            return arg + ',' + self

        self.context.register_function(concat_right, 'concat1')
        self.context.register_function(concat_left, 'concat2')
        self.assertEquals('abc,qwe', self.eval('abc.concat1(qwe)'))
        self.assertEquals('qwe,abc', self.eval('abc.concat2(qwe)'))

    def test_parenthesis(self):
        expression = '(2+3)*2'
        self.assertEquals(10, self.eval(expression))

    def test_as(self):
        @parameter('f', lazy=True)
        def foo(self, f):
            return (self, f())

        self.context.register_function(foo)
        expression = "(random()).as($*10=>random_by_ten).foo($random_by_ten)"
        v = self.eval(expression)
        self.assertTrue(v[1] == v[0] * 10)

    def test_switch(self):
        expression = "$.switch(($>5)=>$, ($>2)=>('_'+string($)), true=>0)"
        self.assertEval(10, expression, 10)
        self.assertEval("_4", expression, 4)
        self.assertEval(0, expression, 1)


if __name__ == '__main__':
    unittest.main()
