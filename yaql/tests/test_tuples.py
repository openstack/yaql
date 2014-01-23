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
from yaql.tests import YaqlTest


class TestTuples(YaqlTest):
    def test_build_tuple(self):
        expression = 'a=>b'
        self.assertEquals(('a', 'b'), self.eval(expression))

    def test_build_triple_tuple(self):
        expression = 'a=>b=>c'
        self.assertEquals(('a', 'b', 'c'), self.eval(expression))

    def test_build_5x_tuple(self):
        expression = 'a=>b=>c=>d=>e'
        self.assertEquals(('a', 'b', 'c', 'd', 'e'), self.eval(expression))

    def test_build_nested_tuple1(self):
        expression = 'a=>(b=>c)'
        self.assertEquals(('a', ('b', 'c')), self.eval(expression))

    def test_build_nested_tuple2(self):
        expression = '(a=>b)=>(c=>d)'
        self.assertEquals((('a', 'b'), ('c', 'd')), self.eval(expression))

    def test_build_nested_tuple3(self):
        expression = '(a=>b)=>(c=>d)=>(e=>f)'
        self.assertEquals((('a', 'b'), ('c', 'd'), ('e', 'f')),
                          self.eval(expression))

    def test_build_nested_tuple4(self):
        expression = 'a=>(b=>c)=>(d=>(e=>f=>g=>h))=>i'
        self.assertEquals(('a', ('b', 'c'), ('d', ('e', 'f', 'g', 'h')), 'i'),
                          self.eval(expression))

    def test_tuple_precedence(self):
        expression1 = 'a=>2+3'
        expression2 = '2+3=>a'
        self.assertEquals(('a', 5), self.eval(expression1))
        self.assertEquals((5, 'a'), self.eval(expression2))



if __name__ == '__main__':
    unittest.main()
