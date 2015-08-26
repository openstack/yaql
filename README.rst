YAQL: Yet Another Query Language
================================

YAQL (Yet Another Query Language) is an embeddable and extensible query
language, that allows performing complex queries against arbitrary objects. It
has a vast and comprehensive standard library of frequently used querying
functions and can be extend even further with user-specified functions. YAQL is
written in python and is distributed via PyPI.

Quickstart
----------
Install the latest version of yaql:

.. code-block:: console

    pip install yaql>=1.0.0
..

Run yaql REPL:

.. code-block:: console

    yaql
..

Load a json file:

.. code-block:: console

    yaql> @load my_file.json
..

Check it loaded to current context, i.e. `$`:

.. code-block:: console

    yaql> $

..

Run some queries:

.. code-block:: console

    yaql> $.customers
    ...
    yaql> $.customers.orders
    ...
    yaql> $.customers.where($.age > 18)
    ...
    yaql> $.customers.groupBy($.sex)
    ...
    yaql> $.customers.where($.orders.len() >= 1 or name = "John")
..

Project Resources
-----------------

* `Official Documentation <http://yaql.readthedocs.org>`_

* Project status, bugs, and blueprints are tracked on
  `Launchpad <https://launchpad.net/yaql>`_


License
-------

Apache License Version 2.0 http://www.apache.org/licenses/LICENSE-2.0
