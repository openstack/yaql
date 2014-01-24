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

import unittest
from yaql.language.engine import parameter
from yaql.language.exceptions import YaqlExecutionException
from yaql.tests import YaqlTest


class Foobar():
    def __init__(self, prompt):
        self.prompt = prompt
        pass

    @parameter('value')
    def foo(self, value):
        return "%s: %s" % (self.prompt, str(value).upper())

    def bar(self, another_value):
        return "%s: %s" % (self.prompt, str(another_value).lower())


class TestObjects(YaqlTest):
    def test_registering_decorated_class_method(self):
        self.context.register_function(Foobar.foo, 'foo')
        self.assertEquals(1, len(self.context.get_functions('foo', 2)))

    def test_registering_undecorated_class_method(self):
        self.context.register_function(Foobar.bar, 'bar')
        self.assertEquals(1, len(self.context.get_functions('bar', 2)))

    def test_calling_decorated_class_method(self):
        self.context.register_function(Foobar.foo, 'foo')
        self.context.register_function(Foobar.bar, 'bar')
        expression = '$.foo(aBc)'
        expression2 = '$.bar(aBc)'
        data = Foobar("foobar")
        self.assertEquals('foobar: ABC', self.eval(expression, data))
        self.assertEquals('foobar: abc', self.eval(expression2, data))

    def test_calling_undecorated_class_method(self):
        self.context.register_function(Foobar.foo, 'foo')
        self.context.register_function(Foobar.bar, 'bar')
        expression = '$.bar(aBc)'
        data = Foobar("foobar")
        self.assertEquals('foobar: abc', self.eval(expression, data))

    def test_calling_decorated_class_methods_for_invalid_objects(self):
        self.context.register_function(Foobar.foo, 'foo')
        expression = '$.foo(aBc)'
        self.assertRaises(YaqlExecutionException, self.eval, expression, "str")
        self.assertRaises(YaqlExecutionException, self.eval, expression,
                          object())

if __name__ == '__main__':
    unittest.main()
