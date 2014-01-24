#    Copyright (c) 2013 Mirantis, Inc.
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
import yaql
from yaql.language.utils import limit


class YaqlTest(unittest.TestCase):
    def setUp(self):
        self.context = yaql.create_context()

    def eval(self, expression, data=None, context=None):
        res = yaql.parse(expression).evaluate(data=data,
                                              context=context or self.context)
        if isinstance(res, types.GeneratorType):
            return limit(res)
        else:
            return res

    def assertEval(self, value, expression, data=None, context=None):
        self.assertEquals(value, self.eval(expression, data, context))
