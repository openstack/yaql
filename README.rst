YAQL - Yet Another Query Language
=================================

At the beginning of millennium the growing trend towards data formats standardization and application integrability made
XML extremely popular. XML became lingua franca of the data. Applications tended to process lots of XML files ranging
from small config files to very large datasets. As these data often had a complex structure with many levels of
nestedness it is quickly became obvious that there is a need for specially crafted domain specific languages to query
these data sets. This  is how XPath and later XQL were born.

With later popularization of REST services and Web 2.0 JSON started to take XML’s place. JSON’s main advantage (besides
being simpler than XML) is that is closely reassembles data structures found in most programming languages (arrays,
dictionaries, scalars) making it very convenient for data serialization. As JSON lacked all the brilliant XML-related
technologies like XSLT, XML Schema, XPath etc. various attempts to develop similar languages for JSON were made. One of
those efforts was JSONPath library developed in 2007 by Stefan Gössner. Initial implementation was for PHP and
JavaScript languages, but later on ports to other languages including Python were written.

JSONPath allows navigation and querying, well, JSONs.
Suppose we have JSON as in following:

    {
      "customers": [
      {
        "customer_id": 1,
        "name": "John",
        "orders": [{
          "order_id": 1,
          "item": "Guitar",
         "quantity": 1
        }]
      },{
       "customer_id": 2,
       "name": "Paul",
       "orders": [ {
          "order_id": 2,
          "item": "Banjo",
          "quantity": 2
         },{
         "order_id": 3,
         "item": "Piano",
         "quantity": 1
        }]
      }
     ]
    }


then

`jsonpath(data, "$.customers[0].name") -> [‘John’]`
`jsonpath(data, "$.customers[*].orders[*].order_id") -> [1, 2, 3]`

But what if we need, for example to find order having ID = 2? Here is how it done in JSONPath:

`jsonpath(data, "$.customers[*].orders[?(@.order_id == 2)") ->  [{'order_id': 2, 'item': 'Banjo', 'quantity': 2}]`

The construct `[?(expression)]` allows to filter items using any Python expression in our case. `@` character is
replaced with current value and then the whole expression is evaluated. Evaluation of arbitrary Python expression
requires using `eval()` function unless one wants to develop his own complete parser and interpreter of Python
programming language. Needless to say that `eval()` is a great security breach. If JSONPath expressions are used to
simplify program logic it would not be a big deal, but what if JSONPath is written by program users?

JSONPath expression is just a plain string. There is no such concept as parameter. That is if one want to find order
having ID = some variable value he has to dynamically construct expression string using string formatting or
concatenation. And again that is might be okay for internal usage but would became difficult for external usage and also
open the doors for injection attacks (remember SQL injection?)

Another limitation of JSONPath is JSON itself. Technically speaking JSONPath operates not on the JSON itself (i.e. text
representation) but on a JSON-like object model that is mixture of arrays, dictionaries and scalar values. But what is
one want to query object model consisting of custom objects? What if some parts of this model are dynamically computed?
Or the model is a graph rather than a tree?

It seems like JSONPath is good enough to use in Python code when you can `eval()` things and have many helper function
to work with data besides JSONPath capabilities but is not enough for external use when you need to have sufficient
power to query model without manual coding and have it still secure.
This is why we designed YAQL. YAQL follows the JSONPath ideas and has very similar syntax but offers much more for data
querying.

Expressions are quite similar to JSONPath. Here is how examples above can be translated to YAQL:

`$.customers[0].name -> $.customers[0].name (no change)`
`$.customers[*].orders[*].order_id -> $.customers.orders.order_id`

the main addition to JSONPath is functions and operators. Consider the following YAQL expressions:

`$.customers.orders[$.quantity > 0].quantity.sum() -> 4`
`$.customers.orders.select($.quantity * $.quantity).sum() -> 6`
`$.customers.orders.order_id.orderDesc($) -> [3, 2, 1]`
`$.customers.orders.order_id.orderDesc($).take(2) -> [3, 2]`
`$.customers.orders.order_id.orderDesc($).first() -> 3`

Does it mean that YAQL has large built-in function and operator library?. Yes, YAQL library has a out of the box large
set of commonly used functions. But they are not built-in. All the functions and operators (which are also function:
`a + b = operator_+(a, b)` etc) are user-supplied. User is free to add other functions that could be used in expressions
and to remove standard ones.

JSONPath library needs 2 arguments - input JSON data and an a expression. YAQL library requires third
parameter - context.

Context is a repository of functions and variables that can be used in expressions. So all the functions above are just
ordinary Python functions that are registered in Context object. But because they all need to be registered in Context
user can always customize them, add his own model-specific ones and have full control over the expression evaluation.
