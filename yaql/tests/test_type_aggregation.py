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

import six

from yaql.language import exceptions
from yaql.language import specs
from yaql.language import yaqltypes
import yaql.tests


class TestTypeAggregation(yaql.tests.TestCase):
    def test_not_of_type(self):
        """
        The test type of test

        Args:
            self: (todo): write your description
        """
        @specs.parameter('arg', yaqltypes.NotOfType(int))
        def foo(arg):
            """
            Returns true if arg is a valid python function.

            Args:
                arg: (int): write your description
            """
            return True

        self.context.register_function(foo)
        self.assertTrue(self.eval('foo($)', data='abc'))
        self.assertTrue(self.eval('foo($)', data=[1, 2]))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo($)', data=123)
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo($)', data=True)

    def test_chain(self):
        """
        Evaluate the chain.

        Args:
            self: (todo): write your description
        """
        @specs.parameter(
            'arg', yaqltypes.Chain(yaqltypes.NotOfType(bool), int))
        def foo(arg):
            """
            Returns true if arg is a valid python function.

            Args:
                arg: (int): write your description
            """
            return True

        self.context.register_function(foo)
        self.assertTrue(self.eval('foo($)', data=123))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo($)', data=True)
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo($)', data='abc')

    def test_any_of(self):
        """
        Test if any of any test is true.

        Args:
            self: (todo): write your description
        """
        @specs.parameter(
            'arg', yaqltypes.AnyOf(six.string_types, yaqltypes.Integer()))
        def foo(arg):
            """
            Return true if arg is a string.

            Args:
                arg: (int): write your description
            """
            if isinstance(arg, six.string_types):
                return 1
            if isinstance(arg, int):
                return 2

        self.context.register_function(foo)
        self.assertEqual(1, self.eval('foo($)', data='abc'))
        self.assertEqual(2, self.eval('foo($)', data=123))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo($)', data=True)
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo($)', data=[1, 2])
