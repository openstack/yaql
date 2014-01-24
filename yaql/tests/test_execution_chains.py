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

from yaql.language.exceptions import YaqlException, YaqlExecutionException
from yaql.tests import YaqlTest
from yaql.language.engine import context_aware, parameter


def f4(self):
    return 'f4({0})'.format(self)


@context_aware
def f3(self, context):
    context.register_function(f4, 'f4')
    return 'f3({0})'.format(self)


@context_aware
def f2(self, context):
    context.register_function(f3, 'f3')
    return 'f2({0})'.format(self)


@context_aware
def f1(self, context):
    context.register_function(f2, 'f2')
    return 'f1({0})'.format(self)


@context_aware
def override_with_caps(self, context):
    context.register_function(lambda self: "data is: " + self.upper(), 'print')
    return self


def _print(self):
    return "data is: %s" % self

@parameter('self', arg_type=types.StringType)
def print_string(self):
    return "print %s" % self


class TestExecutionChain(YaqlTest):
    def setUp(self):
        super(TestExecutionChain, self).setUp()

        self.context.register_function(f1, 'f1')
        self.context.register_function(_print, 'print')
        self.context.register_function(override_with_caps, 'caps_on')


    def test_chain1(self):
        expression = 'f1(abc).f2().f3()'
        self.assertEquals('f3(f2(f1(abc)))', self.eval(expression))

    def test_chain2(self):
        expression = 'abc.f1().f2().f3().f4()'
        self.assertEquals('f4(f3(f2(f1(abc))))', self.eval(expression))

    def test_chain3(self):
        expression = 'abc.f2().f3()'
        self.assertRaises(YaqlException, self.eval, expression)

    def test_chain4(self):
        expression = 'abc.f4().f3().f2().f1()'
        self.assertRaises(YaqlException, self.eval, expression)

    def test_chain5(self):
        expression = 'abc.f1() + abc.f2()'
        self.assertRaises(YaqlException, self.eval, expression)

    def test_override(self):
        expression1 = 'abc.print()'
        expression2 = 'abc.caps_on().print()'
        self.assertEquals("data is: abc", self.eval(expression1))
        self.assertEquals("data is: ABC", self.eval(expression2))

    def test_override_and_forget(self):
        expression = "abc.caps_on().print() + ', but ' + abc.print()"
        self.assertEquals("data is: ABC, but data is: abc",
                          self.eval(expression))

    def test_self_validation(self):
        good_expression = "abc.print_string()"
        wrong_expression = "123.print_string()"
        self.context.register_function(print_string)
        self.assertEval("print abc", good_expression)  # self is valid string
        self.assertRaises(YaqlExecutionException, self.eval, wrong_expression)




if __name__ == '__main__':
    unittest.main()
