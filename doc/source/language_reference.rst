Language reference
==================

YAQL is a single expression language and as such does not have any block
constructs, line formatting, end of statement marks or comments. The expression
can be of any length. All whitespace characters (including newline) that are
not enclosed in quote marks are stripped. Thus, the expressions may span
multiple lines.

Expressions consist of:

* Literals
* Keywords
* Variable access
* Function calls
* Binary and unary operators
* List expressions
* Dictionary expressions
* Index expressions
* Delegate expressions

Terminology
~~~~~~~~~~~

* `YAQL` - the name of the language - acronym for `Yet Another Query Language`

* `yaql` - Python implementation of the YAQL language (this package)

* `expression` - a YAQL query that takes context as an input and produces
  result value

* `context` - an object that (directly or indirectly) holds all the data
  available to expression and all the function implementations accessible to
  expression

* `host` - the application that hosts the yaql interpreter. The host uses yaql
  to evaluate expressions, provides initial data, and decides which functions
  are going to be available to the expression. The host has ultimate power
  to customize yaql - provide additional functions, operators, decide not to
  use standard library or use only parts of it, override function and operator
  behavior

* `variable` - any data item that is available through the context

* `function` - a Python callable that is exposed to the YAQL expression and
  can be called either explicitly or implicitly

* `delegate` - a Python callable that is available as a context variable (in
  expression data rather than registered in context)

* `operator` - a form of implicit function on one (unary operator) or two
  (binary operator) operands

* `alphanumeric` - consists of latin letters and digits (`A-Z`, `a-z`, `0-9`)


Literals
~~~~~~~~

Literals refer to fixed values in expressions. YAQL has the following literals:

* Integer literals: ``123``
* Floating point literals: ``1.23``, ``1.0``
* Boolean and null literals represented by `keywords` (see below)
* String literals enclosed in either single (') or double (") quotes:
  ``"abc"``, ``'def'``. The backslash (\) character is used to escape
  characters that otherwise have a special meaning, such as newline, backslash
  itself, or the quote character
* Verbatim strings enclosed in back quote characters, for example ```abc```,
  are used to suppress escape sequences. This is equivalent to ``r'strings'``
  in Python and is especially useful for regular expressions


Keywords
~~~~~~~~

Keyword is a sequence of characters that conforms to the following criteria:

* Consists of non-zero alphanumeric characters and an underscore (`_`)
* Doesn't start with a digit
* Doesn't start with two underscore characters (`__`)
* Is not enclosed in quote marks of any type

YAQL has only three predefined keywords: `true`, `false`, and `null` that have
the value of similar JSON keywords.

There are also four keyword operators: `and`, `or`, `not`, `in`. However, this
list is not fixed. The yaql host may decide to have additional keyword
operators or not to have any of the four aforementioned keywords.

All other keywords have the value of their string representation. Thus, except
for the predefined keywords and operators they can be considered as string
literals and can be used anywhere where string is expected. However the
opposite is not true. That is, keywords can be used as string literals but
string literals cannot be used where a token is expected.

Examples:

* ``John + Snow`` - the same as ``"John" + "Snow"``
* ``true + love`` - syntactically valid, but cannot be evaluated because
  there is no plus operator that accepts boolean and string (unless you define
  one)
* ``not true`` - evaluates to `false`, `not` is an operator
* ``"foo"()`` - invalid expression because the function name must be a token
* ``John Snow`` - invalid expression - two tokens with no operator between
  them


Variable access
~~~~~~~~~~~~~~~

Each YAQL expression is a function that takes inputs (arguments) and produces
the result value (usually by doing some computations on those inputs).
Expressions get the input through a `context` - an object that holds all the
data and a list of functions, available for expression.

Besides the argument values, expressions may populate additional data items
to the context. All these data are collectively known as a `variables` and
available to all parts of an expression (unless overwritten with another
value).

The syntax for accessing variable values is ``$variableName`` where
`variableName` is the name of the variable. Variable names may consist of
alphanumeric and underscore characters only. Unlike tokens, variable names
may start with digit, any number of underscores and even be an empty string.
By convention, the first (usually the single) function parameter is accessible
through ``$`` expression (i.e. empty string variable name) which is an alias
for ``$1``. The usual case is to pass the main expression data in a single
structure (document) and access it through the ``$`` variable.

If the variable with given name is not provided, it is assumed to be `null`.
There is no built-in syntax to check if a variable exists to distinguish cases
where it does not and when it is just set to null. However in the future such a
function might be added to yaql standard library.

When the yaql parser encounters the ``$variable`` expression, it automatically
translates it to the ``#get_context_data("$variable")`` function call.
By default, the `#get_context_data` function returns a variable value from the
current context. However the yaql host may decide to override it and provide
another behavior. For example, the host may try to look up the value in an
external data source (database) or throw an exception due to a missing
variable.


Function calls
~~~~~~~~~~~~~~

The power of YAQL comes from the fact that almost everything in YAQL is a
function call (explicit or implicit) and any function may be overridden
by the host. In YAQL there are two types of functions:

* `explicit function` - those that can be called from expressions

* `implicit (system) functions` - functions with predefined names that get
  called upon some operations. For example, ``2 + 3`` is translated to
  ``#operator_+(2, 3)``. In this case, `#operator_+` is the name of the
  implicit function. However, because ``#operator_+(2, 3)`` is not a valid YAQL
  expression (because of `#`), implicit functions cannot be called explicitly
  but still can be redefined by the host.

The syntax for explicit function is:

.. productionlist::
   call: funcName "(" [parameters] ")"
   funcName: token
   parameters: positionalParameters |
             : keywordParameters |
             : positionalParameters "," keywordParameters
   positionalParameters: parameter ("," parameter)*
   parameter: expression | empty-string
   keywordParameters: keywordParameter ("," keywordParameter)
   keywordParameter: parameterName "=>" expression
   parameterName: token

In simple words:

* The function name must be a token.
* Parameters may be positional, keyword or both. But keyword parameters
  may not come before positional.
* Positional parameters can be skipped if they have a default value, for
  example, ``foo(1,,3)``.
* Keyword arguments must have a token name that must match the parameter name
  in the function declaration. Therefore, you must know the function signature
  for the right name.

Examples:

* ``foo(2 + 3)``
* ``bar(hello, world)``
* ``baz(a,b, kwparam1 => c, kwparam2 => d)``

Functions have ultimate control over how they can be called. In particular:

* Each parameter may (and usually does) have an associated type check. That is,
  the function may specify that the expected parameter type and if it can be
  null.
* Usually, any parameters can be passed either by positional or keyword syntax.
  However, function declaration may force one particular way and make it
  positional-only or keyword-only.
* A function may have a variable number of positional (aka `*args`) and/or
  keyword (aka `**kwarg`) arguments.
* In most languages, function arguments are evaluated prior to function
  invocation. This is not always true in YAQL. In YAQL, a function may declare
  a lazy argument. In this case, it is not evaluated and the function
  implementation receives a passed value as a callable or even as an AST,
  depending on how the parameter was declared. Thus in YAQL there is no special
  syntax for lambdas. ``foo($ + 1)`` may mean either "call `foo` with value of
  ``$ + 1``" or "call `foo` with expression ``$ + 1`` as a parameter". In the
  latter case it corresponds to ``foo(lambda *args, **kwargs: args[0] + 1)`` in
  Python. Actual argument interpretation depends on the parameter declaration.
* Function may decide to disable keyword argument syntax altogether. For such
  functions, the ``name => expr`` expression will be interpreted as a
  positional parameter ``yaql.language.utils.MappingRule(name, expr)`` and
  the left side of `=>` can be any expression and not just a keyword. This
  allows for functions like ``switch($ > 0 => 1, $ < 0 => -1, $ = 0 => 0)``.

Additionally, there are three subtypes of explicit functions. Suppose that
there is a declared function ``foo(string, int)``. By default, the syntax to
call it will be ``foo(something, 123)``. But it can be declared as a `method`.
In this case, the syntax is going to be ``something.foo(123)``. Because of the
type checking, ``something.foo(123)`` will work since `something` is a
string, but not the ``123.foo(456)``. Thus `foo` becomes a method of a string
type.

A function may also be declared as being an extension method. If foo were to be
declared as an extension method it could be called both as a function
(``foo(string, int)``) and as a method (``something.foo(123)``).

YAQL makes use of a full function signature to determine which function
implementation needs to be executed. This allows several overloads of the same
function as long as they differ by parameter count or parameter type,
or anything else that allows unambiguous identification of the right overload
from the function call expression. For example, ``something.foo(123)`` may
be resolved to a completely different implementation of `foo` from that in
``foo(something, 123)`` if there are two functions with the name `foo` present
in the context, but one of them was declared as a function while the other as
a method. If several overloads are equally suitable for the call expression,
an `AmbiguousFunctionException` or `AmbiguousMethodException` exception gets
raised.


Operators
~~~~~~~~~

YAQL has both binary and unary operators, like most other languages do.
Parentheses and `=>` sequence are not considered as operators and handled
internally by the yaql parser. However, it is possible to configure yaql to use
sequence other than `=>` for that purpose.

The list of available operators is not fixed and can be modified by the host.
The following operators are available by default:

Binary operators:

+--------------------------+---------------------------------+
| Group                    | Operators                       |
+==========================+=================================+
| math operators           | `+`, `-`, `*`, `/`, `mod`       |
+--------------------------+---------------------------------+
| comparision operators    | `>`, `<`, `>=`, `<=`, `=`, `!=` |
+--------------------------+---------------------------------+
| logical operators        | `and`, `or`                     |
+--------------------------+---------------------------------+
| method/member access     | `.`, `?.`                       |
+--------------------------+---------------------------------+
| regex operators          | `=~`, `!~`                      |
+--------------------------+---------------------------------+
| membership operator      | `in`                            |
+--------------------------+---------------------------------+
| context passing operator | `->`                            |
+--------------------------+---------------------------------+


Unary operators:

+--------------------------+---------------------------------+
| Group                    | Operators                       |
+==========================+=================================+
| math operators           | `+`, `-`                        |
+--------------------------+---------------------------------+
| logical operators        | `not`                           |
+--------------------------+---------------------------------+


YAQL supports for both prefix and suffix unary operators. However, only the
prefix operators are provided by default.

In YAQL there are no built-in operators. The parser is given a list of all
possible operator names (symbols), their associativity, precedence, and type,
but it knows nothing about what operators are applicable for what operands.
Each time a parser recognizes the ``X OP Y`` construct and `OP` is a known
binary operator name, it translates the expression to ``#operator_OP(X, Y)``.
Thus. ``2 + 3`` becomes ``#operator_+(2, 3)`` where `#operator_+` is an
implicit function with several implementations including the one for number
addition and defined in standard library. The host may override it and even
completely disable it. For unary operators, ``OP X`` (or ``X OP`` for suffix
unary operators) becomes ``#unary_operator_OP(X)``.

Upon yaql parser initialization, an operator might be given an alias name.
In such cases, ``X OP Y`` is translated to ``*ALIAS(X, Y)`` and ``OP X`` to
``*ALIAS(X)``. This decouples the operator implementation from the operator
symbol. For example, the `=` operator has the `equal` alias. The host may
configure yaql to have the `==` operator instead of `=` keeping the same alias
so that operator implementation and all its consumers work equally well for the
new operator symbol. In default configuration only `=` and `!=` operators have
alias names.

For information on default operators, see the YAQL standard library reference.


List expressions
~~~~~~~~~~~~~~~~

List expressions have the following form:

.. productionlist::
   listExpression: "[" [expressions] "]"
   expressions: expression ("," expression)*

When a yaql parser encounters an expression of the form ``[A, B, C]``, it
translates it into ``#list(A, B, C)`` (for arbitrary number of arguments).

Default `#list` function implementation in standard library produces a list
(tuple) comprised of given elements. However, the host might decide to give it
a different implementation.


Map expressions
~~~~~~~~~~~~~~~

Map expressions have the following form:

.. productionlist::
   mapExpression: "{" [mappings] "}"
   mappings: mapping ("," mapping)*
   mapping: expression "=>" expression

When a yaql parser encounters an expression of the form ``{A => X, B => Y}``,
it translates it into ``#map(A => X, B => Y)``.

The default `#map` implementation disables the keyword arguments syntax and
thus receives a variable length list of mappings, which allows dictionary
keys to be expressions rather than a keyword. It returns a (frozen) dictionary
that itself can be used as a key in another map expression. For example,
``{{a => b} => {[2 + 2, 2 * 2] => 4}}`` is a valid YAQL expression though
yaql REPL utility will fail to display its output due to the fact that it is
not JSON-compatible.


Index expressions
~~~~~~~~~~~~~~~~~

Index expressions have the following form:

.. productionlist::
   indexExpression: expression listExpression


Examples:

* ``[1, 2, 3][0]``
* ``$arr[$index + 1]``
* ``{foo => 1, bar => 2}[foo]``

When a yaql parser encounters such an expression, it translates it into
``#indexer(expression, index)``.

The standard library provides a number of `#indexer` implementations for
different types.

The right side of the index expression is a list expression. Therefore, an
expression like ``$foo[1, x, null]`` is also a valid YAQL expression and will
be translated to ``#indexer($foo, 1, x, null)``. However, any attempt to
evaluate such expression will result in `NoMatchingFunctionException` exception
because there is no `#indexer` implementation that accepts such arguments
(unless the host defines one).


Delegate expressions
~~~~~~~~~~~~~~~~~~~~

Delegate expressions is an optional language feature that is disabled by
default. It makes possible to pass delegates (callables) as part of the context
data and invoke them from the expression. It has the same syntax as explicit
function calls with the only difference being that instead of function name
(keyword) there is a non-keyword expression that must produce the delegate.

Examples:

* ``$foo(1, arg => 2)`` - call delegate returned by ``$foo`` with parameters
  ``(1, arg => 2)``

* ``[$foo, $bar][0](x)`` - the same as ``$foo(x)``

* ``foo()()`` - can be written as ``(foo())()`` - ``foo()`` must return a
  delegate

Delegate expressions are translated into ``#call(callable, arguments)``.
Thus ``$foo(1, 2)`` becomes ``#call($foo, 1, 2)``.

The default implementation of ``#call`` invokes the result of the evaluation
of its first arguments with the given arguments.
