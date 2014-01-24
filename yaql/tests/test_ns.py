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
from yaql.functions import ns
from yaql.tests import YaqlTest


class TestNS(YaqlTest):
    def setUp(self):
        def foo(self):
            return "bar: %s" % self

        super(TestNS, self).setUp()
        ns.add_to_context(self.context)
        namespace = ns.Namespace("com.example.yaql.namespace", 'name',
                                 'composite name', 'function_name')
        ns.get_resolver(self.context).register('nms', namespace)
        self.context.\
            register_function(foo, 'com.example.yaql.namespace.function_name')

    def test_resolve(self):
        self.assertEval("com.example.yaql.namespace.name", 'nms:name')
        self.assertEval("com.example.yaql.namespace.composite name",
                        "nms:'composite name'")
        self.assertEval("com.example.yaql.namespace.function_name",
                        'nms:function_name')

    def test_unable_to_resolve(self):
        self.assertRaises(ns.NamespaceResolutionException, self.eval,
                          'nms2:name')

    def test_unable_to_validate(self):
        self.assertRaises(ns.NamespaceValidationException, self.eval,
                          'nms:line')

    def test_namespace_function_call(self):
        self.assertEval("bar: abc", 'abc.nms:function_name()')

    if __name__ == '__main__':
        unittest.main()
