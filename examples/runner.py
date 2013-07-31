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

import collections
from examples import testdata, ns_functions
import yaql

# DEPRECATED. Use cli to run samples

context = yaql.create_context()
ns_functions.register_in_context(context)
data = testdata.data

expression_list = [
    "$.services.join($.users, $1.yaql:owner=$2.id, dict('Service Name'=>$1.yaql:name,'User email'=>$2.email, 'Parent type'=>$1.yaql:parent_service))[$.'Parent type'=ex:Service0]",
    "range(0, 10 * random()).select(dict(num => $)).list()",
    "range(0).select(random()).takeWhile($ < 0.9).sum()",
]

parsed_list = [yaql.parse(expr) for expr in expression_list]
results = [expr.evaluate(data, context) for expr in parsed_list]

i = 1
for res in results:
    print "result #{0}".format(i)
    i += 1
    if isinstance(res, collections.Iterable):
        for r in res:
            print r
    else:
        print res

