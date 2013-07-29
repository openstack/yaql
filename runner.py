import collections
import types
import yaql
import ns_functions
import testdata
import time

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

