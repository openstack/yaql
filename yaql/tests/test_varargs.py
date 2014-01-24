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
from yaql.tests import YaqlTest


def foo(*args):
    return [arg.upper() for arg in args]


def bar(self, *args):
    return [arg + self for arg in args]


@parameter('predicates', lazy=True, function_only=True)
def buz(*predicates):
    i = 1
    for predicate in predicates:
        if predicate(i):
            yield i
        else:
            yield 0
        i += 1


@parameter('predicates', lazy=True, function_only=True)
def qux(self, *predicates):
    return [predicate(self) for predicate in predicates]


class TestVarArgs(YaqlTest):
    def setUp(self):
        super(TestVarArgs, self).setUp()
        self.context.register_function(foo)
        self.context.register_function(bar)
        self.context.register_function(buz)
        self.context.register_function(qux)

    def test_varargs_only(self):
        expression = "foo(abc, cde, qwerty)"
        self.assertEval(['ABC', 'CDE', 'QWERTY'], expression)

    def test_combined_args_and_varargs_as_method(self):
        expression = "data.bar(abc, cde, qwerty)"
        self.assertEval(['abcdata', 'cdedata', 'qwertydata'], expression)

    def test_combined_args_and_varargs_as_function(self):
        expression = "bar(data, abc, cde, qwerty)"
        self.assertEval(['abcdata', 'cdedata', 'qwertydata'], expression)

    def test_predicate_varargs_only(self):
        expression = "buz($>0, $!=2, $=3, $<4)"
        self.assertEval([1, 0, 3, 0], expression)

    def test_predicate_args_and_varargs_as_method(self):
        expression = "10.qux($*2, $/2, $/5.0, $.to_string(), string($))"
        self.assertEval([20, 5, 2.0, "10", "10"], expression)

    def test_predicate_args_and_varargs_as_function(self):
        expression = "qux(10, $*2, $/2, $/5.0, $.to_string(), string($))"
        self.assertEval([20, 5, 2.0, "10", "10"], expression)


if __name__ == '__main__':
    unittest.main()
