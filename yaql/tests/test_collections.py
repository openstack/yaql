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

from yaql.language.exceptions import YaqlException

from yaql.tests import YaqlTest
import yaql.tests.testdata


class TestCollections(YaqlTest):
    def test_get_by_index(self):
        int_list = [1, 2, 3, 4, 5, 6]
        self.assertEquals(4, self.eval('$[3]', int_list))

    def test_where_by_index(self):
        int_list = [1, 2, 3, 4, 5, 6]
        self.assertRaises(YaqlException, self.eval, '$.where(3)', int_list)

    def test_filter_by_predicate(self):
        int_list = [1, 2, 3, 4, 5, 6]
        self.assertEquals([4, 5, 6], list(self.eval('$[$>3]', int_list)))

    def test_filter_by_non_boolean_predicate(self):
        int_list = [1, 2, 3, 4, 5, 6]
        self.assertRaises(YaqlException, self.eval, '$.where($+1)', int_list)

    def test_list_definition(self):
        self.assertEquals([1, 2, 3], self.eval('list(1,2,3)'))

    def test_in(self):
        int_list = [1, 2, 3, 4, 5, 6]
        self.assertTrue(self.eval('4 in $', int_list))

    def test_not_in(self):
        int_list = [1, 2, 3, 4, 5, 6]
        self.assertFalse(self.eval('7 in $', int_list))

    def test_iterable_property_attribution(self):
        data = yaql.tests.testdata.users
        expression = "$.email"
        self.assertEquals(
            ['user1@example.com', 'user2@example.com', 'user3@example.com'],
            self.eval(expression, data))

    def test_iterable_property_attribution_2(self):
        data = yaql.tests.testdata.data
        expression = "$.users.email"
        self.assertEquals(
            ['user1@example.com', 'user2@example.com', 'user3@example.com'],
            self.eval(expression, data))

    def test_iterable_dictionary_attribution(self):
        data = yaql.tests.testdata.data
        expression = "$.services.'com.mirantis.murano.yaql.name'"
        self.assertEquals(['Service1', 'Service2', 'Service3', 'Service4'],
                          self.eval(expression, data))
