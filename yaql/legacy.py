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

import yaql
from yaql.language import factory
from yaql.standard_library import legacy as std_legacy


class YaqlFactory(factory.YaqlFactory):
    def __init__(self, allow_delegates=False):
        # noinspection PyTypeChecker
        super(YaqlFactory, self).__init__(
            keyword_operator=None, allow_delegates=allow_delegates)
        self.insert_operator(
            'or', True, '=>',
            factory.OperatorType.BINARY_LEFT_ASSOCIATIVE, True)

    def create(self, options=None):
        options = dict(options or {})
        options['yaql.convertTuplesToLists'] = False
        options['yaql.iterableDicts'] = True
        return super(YaqlFactory, self).create(options)


def create_context(*args, **kwargs):
    tuples = kwargs.pop('tuples', True)

    context = yaql.create_context(*args, **kwargs)
    context = context.create_child_context()

    std_legacy.register(context, tuples)
    return context
