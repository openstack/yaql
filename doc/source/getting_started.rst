Getting started with YAQL
=========================

Introduction to YAQL
--------------------

YAQL (Yet Another Query Language) is an embeddable and extensible query
language that allows performing complex queries against arbitrary data structures.
`Embeddable` means that you can easily integrate a YAQL query processor in your code. Queries come
from your DSLs (domain specific language), user input, JSON, and so on. YAQL has a
vast and comprehensive standard library of functions that can be used to query data of any complexity.
Also, YAQL can be extended even further with user-specified functions.
YAQL is written in Python and is distributed through PyPI.

YAQL was inspired by Microsoft LINQ for Objects and its first aim is to execute expressions
on the data in memory. A YAQL expression has the same role as an SQL query to databases:
search and operate the data. In general, any SQL query can be transformed to a YAQL expression,
but YAQL can also be used for computational statements. For example, `2 + 3*4` is a valid
YAQL expression.

Moreover, in YAQL, the following operations are supported out of the box:

* Complex data queries
* Creation and transformation of lists, dicts, and arrays
* String operations
* Basic math operations
* Conditional expression
* Date and time operations (will be supported in yaql 1.1)

An interesting thing in YAQL is that everything is a function and any function can
be customized or overridden. This is true even for built-in functions.
YAQL cannot call any function that was not explicitly registered to be accessible
by YAQL. The same is true for operators.

YAQL can be used in two different ways: as an independent CLI tool, and as a
Python module.

Installation
------------

You can install YAQL in two different ways:

#. Using PyPi:

   .. code-block:: console

        pip install yaql

#. Using your system package manager (for example Ubuntu):

   .. code-block:: console

        sudo apt-get install python-yaql

HowTo: Use YAQL in Python
-------------------------

You can operate with YAQL from Python in three easy steps:

* Create a YAQL engine
* Parse a YAQL expression
* Execute the parsed expression

.. NOTE::
    The engine should be created once for a set of operators and parser rules. It can
    be reused for all queries.

Here is an example how it can be done with the YAML file which looks like:

.. code-block:: yaml

      customers_city:
        - city: New York
          customer_id: 1
        - city: Saint Louis
          customer_id: 2
        - city: Mountain View
          customer_id: 3
      customers:
        - customer_id: 1
          name: John
          orders:
            - order_id: 1
              item: Guitar
              quantity: 1
        - customer_id: 2
          name: Paul
          orders:
            - order_id: 2
              item: Banjo
              quantity: 2
            - order_id: 3
              item: Piano
              quantity: 1
        - customer_id: 3
          name: Diana
          orders:
            - order_id: 4
              item: Drums
              quantity: 1

.. code-block:: python

    import yaql
    import yaml

    data_source = yaml.load(open('shop.yaml', 'r'))

    engine = yaql.factory.YaqlFactory().create()

    expression = engine(
        '$.customers.orders.selectMany($.where($.order_id = 4))')

    order = expression.evaluate(data=data_source)

Content of the ``order`` will be the following:

.. code-block:: console

    [{u'item': u'Drums', u'order_id': 4, u'quantity': 1}]

YAQL grammar
------------

YAQL has a very simple grammar:

* Three keywords as in JSON: true, false, null
* Numbers, such as 12 and 34.5
* Strings: `'foo'` and `"bar"`
* Access to the data: $variable, $
* Binary and unary operators: 2 + 2, -1, 1 != 2, $list[1]

Data access
~~~~~~~~~~~

Although YAQL expressions may be self-sufficient, the most important value of YAQL
is its ability to operate on user-passed data. Such data is placed into variables
which are accessible in a YAQL expression as `$<variable_name>`. The `variable_name`
can contain numbers, English alphabetic characters, and underscore symbols. The `variable_name`
can be empty, in this case you will use `$`. Variables can be set prior to executing
a YAQL expression or can be changed during the execution of some functions.

According to the convention in YAQL, function parameters, including input data,
are stored in variables like `$1`, `$2`, and so on. The `$` stands for `$1`.
For most cases, all function parameters are passed in one piece and can be accessed
using `$`, that is why this variable is the most used one in YAQL expressions.
Besides, some functions are expected to get a YAQL expression as one of the
parameters (for example, a predicate for collection sorting). In this case,
passed expression is granted access to the data by `$`.

Strings
~~~~~~~

In YAQL, strings can be enclosed in `"` and `'`. Both types are absolutely equal and
support all standard escape symbols including unicode code-points. In YAQL, both types
of quotes are useful when you need to include one type of quotes into the
other. In addition, ` is used to create a string where only one escape symbol \` is possible.
This is especially suitable for regexp expressions.

If a string does not start with a digit or `__` and contains only digits, `_`, and English letters,
it is called identifier and can be used without quotes at all. An identifier can be used
as a name for function, parameter or property in `$obj.property` case.

Functions
~~~~~~~~~

A function call has syntax of `functionName(functionParameters)`. Brackets are necessary
even if there are no parameters. In YAQL, there are two types of parameters:

* Positional parameters
   ``foo(1, 2, someValue)``
* Named parameters
   ``foo(paramName1 => value1, paramName2 => 123)``

Also, a function can be called using both positional and named parameters: ``foo(1, false, param => null)``.
In this case, named arguments must be written after positional arguments. In
``name => value``, `name` must be a valid identifier and must match the name of
parameter in function definition. Usually, arguments can be passed in both ways,
but named-only parameters are supported in YAQL since Python 3 supports them.

Parameters can have default values. Named parameters is a good way to pass only needed
parameters and skip arguments which can be use default values, also you can simply
skip parameters in function call: ``foo(1,,3)``.

In YAQL, there are three types of functions:

* Regular functions: ``max(1,2)``
* Method-like functions, which are called by specifying an object for which the
   function is called, followed by a dot and a function call: ``stringValue.toUpper()``
* Extension methods, which can be called both ways: ``len(string)``, ``string.len()``

YAQL standard library contains hundreds of functions which belong to one of these types.
Moreover, applications can add new functions and override functions from the standard library.

Operators
~~~~~~~~~

YAQL supports the following types of operators out of the box:

* Arithmetic: `+`. `-`, `*`, `/`, `mod`
* Logical: `=`, `!=`, `>=`, `<=`, `and`, `or`, `not`
* Regexp operations: `=~`, `!~`
* Method call, call to the attribute: `.`, `?.`
* Context pass: `->`
* Indexing: `[ ]`
* Membership test operations: `in`

Data structures
~~~~~~~~~~~~~~~

YAQL supports these types out of the box:


* Scalars

   YAQL supports such types as string, int. boolean. Datetime and timespan
   will be available after yaql 1.1 release.

* Lists

   List creation: ``[1, 2, value, true]``
   Alternative syntax: ``list(1, 2, value, true)``
   List elemenets can be accesessed by index: ``$list[0]``

* Dictionaries

   Dict creation: ``{key1 => value1, true => 1, 0 => false}``
   Alternative syntax: ``dict(key1 => value1, true => 1, 0 => false)``
   Dictionaries can be indexed by keys: ``$dict[key]``. Exception will be raised
   if the key is missing in the dictionary. Also, you can specify value which will
   be returned if the key is not in the dictionary: ``dict.get(key, default)``.

   .. NOTE::
      During iteration through the dictionary, `key` can be called like: ``$.key``

* (Optional) Sets

   Set creation: ``set(1, 2, value, true)``

.. NOTE::
   YAQL is designed to keep input data unchanged. All the functions that
   look as if they change data, actually return an updated copy and keep the original
   data unchanged. This is one reason why YAQL is thread-safe.

Basic YAQL query operations
---------------------------

It is obvious that we can compare YAQL with SQL as they both are designed to solve
similar tasks. Here we will take a look at the YAQL functions which have a direct
equivalent with SQL.

We will use YAML from `HowTo: use YAQL in Python`_ as a data source in our examples.


Filtering
~~~~~~~~~

.. NOTE::

    Analog is SQL WHERE

The most common query to the data sets is filtering. This is a type of
query which will return only elements for which the filtering query is true. In YAQL,
we use ``where`` to apply filtering queries.

.. code-block:: console

    yaql> $.customers.where($.name = John)

.. code-block:: yaml

      - customer_id: 1
        name: John
        orders:
          - order_id: 1
            item: Guitar
            quantity: 1


Ordering
~~~~~~~~

.. NOTE::

    Analog is SQL ORDER BY

It may be required to sort the data returned by some YAQL query. The ``orderBy`` clause will cause
the elements in the returned sequence to be sorted according to the default comparer
for the type being sorted. For example, the following query can be extended to sort
the results based on the profession property.

.. code-block:: console

    yaql> $.customers.orderBy($.name)

.. code-block:: yaml

      - customer_id: 3
        name: Diana
        orders:
          - order_id: 4
            item: Drums
            quantity: 1
      - customer_id: 1
        name: John
        orders:
          - order_id: 1
            item: Guitar
            quantity: 1
      - customer_id: 2
        name: Paul
        orders:
          - order_id: 2
            item: Banjo
            quantity: 2
          - order_id: 3
            item: Piano
            quantity: 1

Grouping
~~~~~~~~

.. NOTE::

    Analog is SQL GROUP BY

The ``groupBy`` clause allows you to group the results according to the key you specified.
Thus, it is possible to group example json by gender.

.. code-block:: console

    yaql> $.customers.groupBy($.name)

.. code-block:: yaml

        - Diana:
          - customer_id: 3
            name: Diana
            orders:
              - order_id: 4
                item: Drums
                quantity: 1
        - Paul:
          - customer_id: 2
            name: Paul
            orders:
              - order_id: 2
                item: Banjo
                quantity: 2
              - order_id: 3
                item: Piano
                quantity: 1
        - John:
          - customer_id: 1
            name: John
            orders:
              - order_id: 1
                item: Guitar
                quantity: 1

So, here you can see the difference between ``groupBy`` and ``orderBy``. We use
the same parameter `name` for both operations, but in the output for ``groupBy``
`name` is located in additional place before everything else.

Selecting
~~~~~~~~~

.. NOTE::

    Analog is SQL SELECT

The ``select`` method allows building new objects out of objects of some collection.
In the following example, the result will contain a list of name/orders pairs.

.. code-block:: console

    yaql> $.customers.select([$.name, $.orders])

.. code-block:: console

        - John:
          - order_id: 1
            item: Guitar
            quantity: 1
        - Paul:
          - order_id: 2
            item: Banjo
            quantity: 2
          - order_id: 3
            item: Piano
            quantity: 1
        - Diana:
          - order_id: 4
            item: Drums
            quantity: 1

Joining
~~~~~~~

.. NOTE::

    Analog is SQL JOIN

The ``join`` method creates a new collection by joining two other collections by
some condition.

.. code-block:: console

    yaql> $.customers.join($.customers_city, $1.customer_id = $2.customer_id, {customer=>$1.name, city=>$2.city, orders=>$1.orders})

.. code-block:: yaml

      - customer: John
        city: New York
        orders:
          - order_id: 1
            item: Guitar
            quantity: 1
      - customer: Paul
        city: Saint Louis
        orders:
          - order_id: 2
            item: Banjo
            quantity: 2
          - order_id: 3
            item: Piano
            quantity: 1
      - customer: Diana
        city: Mountain View
        orders:
          - order_id: 4
            item: Drums
            quantity: 1


Take an element from collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

YAQL supports two general methods that can help you to take elements from collection
``skip`` and ``take``.

.. code-block:: console

    yaql> $.customers.skip(1).take(2)

.. code-block:: yaml

      - customer_id: 2
        name: Paul
        orders:
          - order_id: 2
            item: Banjo
            quantity: 2
          - order_id: 3
            item: Piano
            quantity: 1
      - customer_id: 3
        name: Diana
        orders:
          - order_id: 4
            item: Drums
            quantity: 1

First element of collection
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``first`` method will return the first element of a collection.

.. code-block:: console

    yaql> $.customers.first()

.. code-block:: yaml

    - customer_id: 1
      name: John
      orders:
        - order_id: 1
          item: Guitar
          quantity: 1
