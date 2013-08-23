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
from yaql.exceptions import YaqlSequenceException

MAX_GENERATOR_ITEMS = 100000


def limit(generator, limit=MAX_GENERATOR_ITEMS):
    res = []
    for i in xrange(limit):
        try:
            res.append(generator.next())
        except StopIteration:
            return res
    raise YaqlSequenceException(limit)
