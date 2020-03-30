Customizing and extending yaql
==============================

Configuring yaql parser
-----------------------

yaql has two main points of customization:

* yaql engine settings allow one to configure the query language and execution
  flags shared by all queries that are processed by the same YAQL parser. This
  includes the list of available operators, yaql resources quotas, and other
  engine parameters.
* By customizing the yaql context object, one can change the list of available
  functions (add new, override existing) and change naming conventions.

Engine options are supplied to the `yaql.language.factory.YaqlFactory` class.
YaqlFactory is used to create instances of the YaqlEngine, that is the YAQL
parser. This is done by calling the `create` method of the factory. Once the
engine is created, it captures all the factory options so that they cannot be
changed for that particular parser any longer. In general, it is recommended
to have one yal engine instance per application, because construction of the
parser is an expensive operation and the parser has no internal state and thus
can be reused for several queries, including in different threads. However, the
host may have several YAQL parsers for different option sets or dialects.

On the contrary, the context object is cheap to create and is mutable by
design, since it holds the input data for the query. In most cases it is a good
idea to execute each query in its own context, although all such contexts might
be the children of some other, fixed context that is created just once.


Customizing operators
~~~~~~~~~~~~~~~~~~~~~

`YaqlFactory` object holds an operator table that is recognized by the parser
produced by it. By default, it is prepopulated with standard operators and
most applications never need to do anything here. However, if the host wants
to have some custom operator symbol available in its expressions, this table
needs to be modified. `YaqlFactory` holds the operator symbols and other
information about the operator that is relevant to the parser, but not the
implementations. The implementations (what operators actually do) are put
in the `context` and can be configured for each expression, but the list of
available operator symbols cannot be changed for the parser once it has been
built.

Each operator in the table is represented by the tuple
`(op_symbols, op_type, op_alias)`:

* op_symbols are the operator symbols. There are no limitations on how the
  operators can be called as long as they do not contain whitespaces. It can
  be one symbol (like `+`), several symbols (like `=~`) or even a word
  (like `not`). List/index and dictionary expressions require `[]` and `{}`
  binary left associative operators to be present in the table. Otherwise
  corresponding constructions will not work (and can be disabled by removing
  corresponding operators from the table)
* op_type is one of the values in `yaql.language.factory.OperatorType`
  enumeration: BINARY_LEFT_ASSOCIATIVE and BINARY_RIGHT_ASSOCIATIVE for binary
  operators, PREFIX_UNARY and SUFFIX_UNARY for unary operators, NAME_VALUE_PAIR
  for the keyword/mapping pseudo-operator (that is `=>`, by default).
* op_alias is the alias name for the operator. See YAQL language reference on
  how operator aliases are used. Aliases are optional and most operators do not
  have it and thus are represented by a tuple of two elements.

Operators are grouped by their precedence. Operators with a higher precedence
come first in the operator table. Operators within the same group have the same
precedence. Groups are separated by an empty tuple (`()`).

The operator table, which is a list of tuples, is available through the
`operators` attribute of the factory and is open for modification. To simplify
the editing, `YaqlFactory` provides the `insert_operator` helper method to
insert an operator before of after some other existing operator to get the
desired precedence.

Execution options
~~~~~~~~~~~~~~~~~

Execution options are the settings and flags that affect execution of each
query and are accessible and processed by both yaql runtime and standard
library functions.

Options are passed to the `create` method of the `YaqlFactory` class in a
plain key-value dictionary. The factory does not process the dictionary but
rather attaches the options to the constructed engine (YAQL parser) after which
they cannot be changed. However, the engine provides a `copy` method that can
be used to clone the engine with different execution options.

The options that are honored by the yaql are:

* `"yaql.limitIterators": <INT>` limit iterators by the given number of
  elements. When set, each time any function declares its parameter to be
  iterator, that iterator is modified to not produce more than a given number
  of items. Also, upon the expression evaluation, all the output collections
  and iterators are limited as well. If not set (or set to -1) the result data
  is allowed to contain endless iterators that would cause errors if the result
  where to be serialized (to JSON or any other format). Default is -1 (do not
  limit).
* `"yaql.memoryQuota": <INT>` - the memory usage quota (in bytes) for all
  data produced by the expression (or any part of it). Default is -1 (do not
  limit).
* `"yaql.convertTuplesToLists": <True|False>`. When set to true, yaql converts
  all tuples in the expression result to lists. The default is `True`.
* `"yaql.convertSetsToLists": <True|False>`. When set to true, yaql converts
  all sets in the expression result to lists. Otherwise the produced result
  may contain sets that are not JSON-serializable. The default is `False`.
* `"yaql.iterableDicts": <True|False>`. When set to true, dictionaries are
  considered to be iterable and iteration over dictionaries produces their
  keys (as in Python and yaql 0.2). Defaults to `False`.

Consumers are free to use their own settings or use the options dictionary to
provide some other environment information to their own custom functions.


Other engine customizations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

`YaqlFactory` class initializer has two optional parameters that can be used
to further customize the YAQL parser:

* `keyword_operator` allows one to configure keyword/mapping symbol. The
  default is `=>`. Ability to pass named arguments can be disabled altogether
  if `None` or empty string is provided.
* `allow_delegates` enables or disables delegate expression parsing. Default
  is False (disabled).

Working with contexts
~~~~~~~~~~~~~~~~~~~~~

Context is an interface that yaql runtime uses to obtain a list of available
functions and variables. Any context object must implement
`yaql.language.contexts.ContextBase` interface and yaql provides several such
implementations ranging from the `yaql.language.contexts.Context` class,
that is a basic context implementation, to contexts that allow one to merge
several other contexts into one or link an existing context into the list of
contexts.

Any context may have a parent context. Any lookup that is done in the context
is also performed in its parent context, extending all the way up its chain of
contexts. During expression evaluation, yaql can create a long chain of
contexts that are all children of the context that was originally passed with
the query.

Most of the yaql customizations are achieved by context manipulations.
This includes:

* Overriding YAQL functions
* Building context chains and evaluating sub-expressions in different
  contexts
* Composing context chains from pre-built contexts
* Having custom `ContextBase` implementations and mixing them with regular
  contexts in the single chain

In fact, it is the context which provides the entry point for expression
evaluation. And thus custom context implementations may completely change
the way queries are evaluated.

There are three ways to create a context instance:

#. Directly instantiate one of `ContextBase` implementations to get an empty
   context
#. Call `create_child_context` method on any existing context object to get a
   child context
#. Use `yaql.create_context` function to creates the root context that is
   prepopulated with YAQL standard library functions

`yaql.create_context` allows one to selectively disable standard library
modules.

Naming conventions
~~~~~~~~~~~~~~~~~~

Naming conventions define how Python functions and parameter names are
translated into YAQL names. Conventions are implementations of the
`yaql.language.conventions.Convention` interface that has just two methods:
one to translate the function name and another to translate the function
parameter name.

yaql has two implementations included:

* `yaql.language.conventions.CamelCaseConvention` that translates Python
  conventions into camel case. For example, it will convert
  `my_func(arg_name)` into `myFunc(argName)`. This convention is used by
  default.

* `yaql.language.conventions.PythonConvention` that leaves function and
  parameter names intact.

Each context, either directly or indirectly through its parent context, is
configured to use some convention. When a function is registered in the
context, its name and parameters are translated with the convention methods.
Also, regardless of convention used, all trailing underscores are stripped
from the names. This makes it possible to define several Python functions that
differ only by trailing underscores and get the same name in YAQL (to create
several overloads of single function). Also, this allow one to have function
or parameter names that would otherwise conflict with Python keywords.

Instance of convention class can be specified as a context initializer
parameter or as a parameter of `yaql.create_context` function. Child contexts
created with the `create_child_context` method inherit their parent convention.

Extending yaql
--------------

Extending yaql with new functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a function to become available to YAQL queries, it must be present in
the provided context object. The default context implementation
(`yaql.language.contexts.Context`) has a `register_function` method to register
the function implementation.

In yaql, all functions are represented by instances of the
`yaql.language.specs.FunctionDefinition` class. FunctionDefinition describes
the complete function signature including:

* Function name
* List of parameters - instances of `yaql.language.specs.ParameterDefinition`
* Function payload (Python callable)
* Function type: function, method or extension method
* The flag to disable the keyword arguments syntax for the function
* Documentation string
* Custom function metadata (dict)

`register_function` method can accept either an instance of
the `FunctionDefinition` class or a regular Python function. In the latter
case, it constructs a `FunctionDefinition` instance from the declaration of
the function using Python introspection. Because a YAQL function signature has
much more information than the Python one, yaql provides a number of function
decorators that can be used to fill the missing properties.

The decorators are located in the `yaql.language.specs` module.
Below is the list of available function decorators:

* ``@name(function_name)``: set function name to be `function_name` rather
  than its Python name
* ``@parameter(...)`` is used to declare the type of one of the function
  parameters
* ``@inject(...)`` is used to declare a hidden function parameter
* ``@method`` declares function to be YAQL method
* ``@extension_method`` declares function to be YAQL extension method
* ``@no_kwargs`` disables the keyword arguments syntax for the function
* ``@meta(name, value)`` appends the `name` attribute with the given value to
  the function metadata dictionary


Specifying function parameter types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When yaql constructs `FunctionDefinition`, it collects all possible information
about its parameters. For each parameter, it records its name, position,
whether it is a keyword-only argument (available in Python 3), whether it is
an `*args` or `**kwargs`, and its default parameter value.

The only parameter attribute that cannot be obtained through retrospection is
the parameter type. For that purpose, yaql has a ``@parameter(name, type)``
decorator that can be used to explicitly declare the parameter type.
`name` must match the name of one of the function parameters, and `type` must
be of the `yaql.language.yaqltypes.SmartType` type.

`SmartType` is the base class for all yaql type descriptors - classes that
check if the value is compatible with the desired type and can do type
conversion between compatible types.

YAQL type system slightly differs from Python's:

* Strings are not considered to be collections of characters
* Booleans are not integers
* Dictionaries are not iterable
* For most of the types one can specify if the `null` (`None`) value is
  acceptable

`yaql.language.yaqltypes` module has many useful smart-type classes. The most
generic smart-type for primitive types is the `PythonType` class, that
validates if the value is instance of a given Python type. Due to the mentioned
differences between YAQL and Python type systems and because
Python types have a lot of nuances (several string types, differences between
Python 2 and Python 3, separation between mutable and immutable type versions:
list-tuple, set-frozenset, dict-FrozenDict, which is missing in Python
and provided by the yaql instead), yaql provides specialized smart-types
for most primitive types:

* `String` - str and unicode
* `Integer`
* `Number` - integer of float
* `DateTime`
* `Sequence` - fixed-size iterable collection, except for the dictionary
* `Iterable` - any iterable or generator
* `Iterator` - iterator over the iterable

And several specialized variants that enforce particular representation in the
YAQL syntax:

* `Keyword`
* `BooleanConstant`
* `NumericConstant`
* `StringConstant`

It is also possible to aggregate several smart-types so that the value can be
of any given type or conform to all of them:

* `AnyOf`
* `Chain`
* `NotOfType`

These three smart-types accept other smart-type(s) as their initializer
parameter(s).

In addition to the smart-types, the second parameter of the `@parameter` can be
a Python type. For example, ``@parameter("name", unicode)`` or
``@parameter("name", unicode, nullable=True)``. In this case the Python type
is automatically wrapped in the `PythonType` smart-type. If nullability is not
specified, yaql tries to infer it from the parameter declaration - it is
nullable only if the parameter has its default value set to `None`.

Lazy evaluated function parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the smart-types from the previous section are for parameters that are
evaluated before the function gets invoked. But sometimes the function might
need the parameter to remain unevaluated so that it can be evaluated by the
function itself, possibly with additional parameters or in a different context.

There are two possible representations of non-evaluated arguments:

* Get it as a Python callable that the function can call to do the evaluation
* Get it as a YAQL expression (AST), that can be analyzed

The first method is available through the `Lambda` smart-type. The parameter,
which is declared as a ``Lambda()``, has an `*args/**kwargs` signature and can
be called from the function: ``parameter(arg1, arg2)``. If it was declared as
``Lambda(with_context=True)`` the function may invoke it in a context, other
than that which is used for the function:
``parameter(new_context, arg1, arg2)``. ``Lambda(method=True)`` specifies
that the parameter must be a method and the caller can specify the receiver
object for it: ``parameter(receiver, arg1, arg2)``. Parameters can also be
combined: ``Lambda(with_context=True, method=True)`` so the callable is
invoked as ``parameter(receiver, new_context, arg1, arg2)``. All supplied
callable arguments are automatically published to the `$1` (`$`), `$2` and
so on context variables for the context in which the callable will be executed.

The second method is available through the `YaqlExpression` smart-type. It
also allows one to request the parameter to be of a particular expression type
rather than an arbitrary YAQL expression.

Auto-injected function parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Besides regular parameters, yaql also supports auto-injected (hidden)
parameters. This is also known as a function parameter dependency injection.
The values of injected parameters come from the yaql runtime rather than from
the caller. Functions use injected parameters to get information on their
execution environment.

Auto-injected parameters are declared using the ``@inject(...)`` decorator,
which has exactly the same signature as `@parameter` with the only difference
being that `@inject` checks that that the supplied smart-type is an instance
of the `yaql.language.yaqltypes.HiddenParameterType` class (in addition to
`SmartType`), whereas the `@parameter` decorator checks that it is not. This
difference exists to clearly distinguish explicitly passed parameters from
those that are injected by the system.

yaql has the following hidden parameter smart types:

* `Context` - injects the current function context object
* `Engine` - injects `YaqlEngine` object that was used to parse the expression.
  Engine object may be used to access execution options or to parse some other
  expression
* `FunctionDefinition` - `FunctionDefinition` object of the function. May be
  used to obtain function metadata and doc-string
* `Delegate` - injects a Python callable to some other YAQL function by its
  name. This is a convenient way to call one YAQL function from another without
  depending on its Python implementation signature and location. The syntax
  is very similar to `Lambda` smart-type
* `Super` - similar to `Delegate` - injects callable to an overload of itself
  from the parent context. Useful when the function overload wants to call its
  base implementation (analogous to Python's ``super()``)
* `Receiver` - injects a method receiver object if the function was called as
  a method and `None` otherwise. Can be used in an extension method to
  distinguish the case, when it was invoked as a method rather than as a
  function. Do not do it without a good reason!
* `YaqlInterface` - injects a convenient wrapper (`YaqlInterface`) around yaql
  functionality, which also encapsulates many of the values above

Auto-injected parameters may appear anywhere in the function signature as they
do not affect caller syntax. Implementations can add additional hidden
parameters without breaking existing queries. However, it is important to
call YAQL function implementations through the yaql mechanisms (such as
`Delegate`), rather than to call their Python implementations directly.

Automatic parameters
~~~~~~~~~~~~~~~~~~~~

In some cases there is no need to declare the parameter at all. yaql uses
parameter name and default value to guess the parameter type if it was not
declared.

If the parameter name is `context` or `__context` it will automatically
be treated as if it was declared as a `Context`. `engine`/`__engine` is
considered as an `Engine`, and `yaql_interface`/`__yaql_interface` is
considered as a `YaqlInterface`.

The host can override this logic by providing a callable to Context's
`register_function` method through the `parameter_type_func` parameter.
When yaql encounters an undeclared parameter, it calls this function, passing
the parameter name as an argument, and expects it to return a smart-type
for the parameter.

If the `parameter_type_func` callable returned `None`, yaql would assume that
the smart type should be `PythonType(object)`, that is anything, except for
the `None` value, unless the parameter had the default value `None`.

Function resolution rules
~~~~~~~~~~~~~~~~~~~~~~~~~

Function resolution rules are used to determine the correct overload of the
function when more than one overload is present in the context. Each time a
function with a given list of parameters is called yaql does the following:

#. Walks through the chain of context objects and collects all the
   implementations with a given name and appropriate type (either functions
   and extension methods or methods and extensions methods, depending on the
   call syntax).
#. All found overloads are organized into layers so that overloads from the
   same context will be put in the same layer whereas overloads from different
   contexts are in different layers. Overloads from contexts that are closer
   to the initial context have precedence over those which were obtained from
   the parent contexts. Also `FunctionDefinition` may have a flag that prevents
   all overload lookups in the parent contexts. If the search encounters an
   overload with such a flag, it does not go any further in the chain.
#. Scan all found overloads and exclude those, that cannot be called by the
   given syntax. This can happen because the overload has more mandatory
   parameters than the arguments in the calling expression, or because it
   passes the argument using the keyword name and no such parameter exists.
#. Validates laziness of overload parameters. If at least one function overload
   has a lazy evaluated parameter all other overloads must have it in the same
   position. Violation of this rule causes an exception to be thrown.
#. All the non-lazy parameters are evaluated. The result values are validated
   by appropriate smart-type instances corresponding to each parameter of
   each overload. All the overloads that are not type-compatible with the
   given arguments are excluded in each layer.
#. Take first non-empty layer. If no such layer exists (that is all the
   overloads were excluded) then throw an exception.
#. If the found layer has more than one overload, then we have an ambiguity.
   In this case an exception is thrown since we cannot unambiguously determine
   the right overload.
#. Otherwise, call the single overload with previously evaluated arguments.


Function development hints
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Avoid side effects in your functions, unless you absolutely have to.
* Do not make changes to the data structures coming from the parameters or the
  context. Functions that modify the data should return the modified copy
  rather than touch the original.
* If you need to make changes to the context, create a child context and
  make them there. It is usually possible to pass the new context to other
  parts of the query.
* Strongly prefer immutable data structures over mutable ones. Use `tuple`s
  rather than `list`s, `frozenset` instead of `set`. Python does not have a
  built-in immutable dictionary class so yaql provides one on its own -
  `yaql.language.utils.FrozenDict`.
* Do not call Python implementation of YAQL functions directly. yaql provides
  plenty of ways to do so.
* Do not reuse contexts between multiple queries unless it is intentional.
  However all of these contexts can be children of a single prepared context.
* Do not register all the custom functions for each query. It is better to
  prepare all the contexts with functions at the beginning and then use
  child contexts for each query executed.
