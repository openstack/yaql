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


class TestMiscellaneous(yaql.tests.TestCase):
    def test_bool_is_not_an_integer(self):
        @specs.parameter('arg', yaqltypes.Integer())
        def foo(arg):
            return arg

        self.context.register_function(foo)
        self.assertEqual(2, self.eval('foo(2)'))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo(true)')
