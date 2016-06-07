YAQL documenter script
======================

YAQL documenter is a script which collects docstrings from given Python package
or module which contains YAQL functions which is properly documented.
It is created to document standard library functions, but also it can be
used to document custom YAQL functions if they follow documentation guideline
for YAQL.

Documentation guideline
-----------------------

1. Provide a description for module itself, or module will be marked as
   ``not documented yet``. For example:

   """
   Whenever an expression is used in the context of boolean operations the
   following values are interpreted as false: ``false``, ``none``, numeric zero of
   any type, empty strings, empty dict, empty list.
   All other values are interpreted as true.
   """

2. YAQL related part of docstring should starts with marker ``:yaql:``.

3. After marker you should first specify a name for function in YAQL.
   For example `operator and`.

4. Next string should contain function description. For example:
   `Returns left operand if it evaluates to false, otherwise right.`

5. After that you can specify its signature using `:signature:`, args,
   args type and code description if you want.

6. Documenter will automatically add `:callAs:` field with value among
   `operator`, `method`, `function`, `function or method`.


Complete example of documented function
---------------------------------------

.. code::

    @specs.parameter('left', yaqltypes.Lambda())
    @specs.parameter('right', yaqltypes.Lambda())
    @specs.name('#operator_and')
    def and_(left, right):
        """:yaql:operator and

        Returns left operand if it evaluates to false, otherwise right.

        :usage: left and right
        :arg left: left operand
        :argType left: any
        :arg right: right operand
        :argType right: any

        .. code::

            yaql> 1 and 0
            0
            yaql> 1 and 2
            2
            yaql> [] and 1
            []
        """
        return left() and right()

..

Documenter script workflow
--------------------------

To add your documentation for YAQL functions you should run documenter script
from the environment where Python package or module contains the functions to
document. In case if you document package other than standard library YAQL it
isn't needed. You can use virtualenv, install it locally or whatever you want.

After that run documenter with the following:

.. console::

    python yaql/contrib/documenter.py --output <file_name> <YAQL.module_path>

..

Here is an example for the default workflow:

.. console::

    python yaql/contrib/documenter.py --output doc/source/standard_library.rst yaql.standard_library

..
