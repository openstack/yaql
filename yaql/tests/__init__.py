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

import testtools

import yaql
from yaql.language import factory
from yaql import legacy


class TestCase(testtools.TestCase):
    _default_engine = None
    _default_legacy_engine = None

    engine_options = {
        'yaql.limitIterators': 100,
        'yaql.memoryQuota': 20000,
        'yaql.convertTuplesToLists': True,
        'yaql.convertSetsToLists': True
    }

    legacy_engine_options = {
        'yaql.limitIterators': 100,
        'yaql.memoryQuota': 20000,
    }

    def create_engine(self):
        func = TestCase._default_engine
        if func is None:
            engine_factory = factory.YaqlFactory(allow_delegates=True)
            TestCase._default_engine = func = engine_factory.create(
                options=self.engine_options)
        return func

    def create_legacy_engine(self):
        func = TestCase._default_legacy_engine
        if func is None:
            engine_factory = legacy.YaqlFactory()
            TestCase._default_legacy_engine = func = engine_factory.create(
                options=self.legacy_engine_options)
        return func

    @property
    def context(self):
        if self._context is None:
            self._context = yaql.create_context(delegates=True)
        return self._context

    @property
    def legacy_context(self):
        if self._legacy_context is None:
            self._legacy_context = legacy.create_context()
        return self._legacy_context

    @context.setter
    def context(self, value):
        self._context = value

    @property
    def engine(self):
        if self._engine is None:
            self._engine = self.create_engine()
        return self._engine

    @property
    def legacy_engine(self):
        if self._legacy_engine is None:
            self._legacy_engine = self.create_legacy_engine()
        return self._legacy_engine

    def setUp(self):
        self._context = None
        self._engine = None
        self._legacy_context = None
        self._legacy_engine = None
        super(TestCase, self).setUp()

    def eval(self, expression, data=None, context=None):
        expr = self.engine(expression)
        context = context or self.context
        context['data'] = data
        return expr.evaluate(data=data, context=context)

    def legacy_eval(self, expression, data=None, context=None):
        expr = self.legacy_engine(expression)
        return expr.evaluate(data=data, context=context or self.legacy_context)

    def legacy_eval_new_engine(self, expression, data=None, context=None):
        expr = self.engine(expression)
        return expr.evaluate(data=data, context=context or self.legacy_context)
