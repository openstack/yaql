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
"""
The module describes branching functions such as switch, case, and others.
"""

from yaql.language import specs
from yaql.language import yaqltypes


@specs.parameter('args', yaqltypes.MappingRule())
@specs.no_kwargs
def switch(*args):
    """:yaql:switch

    Returns the value of the first argument for which the key evaluates to
    true, null if there is no such arg.

    :signature: switch([args])
    :arg [args]: mappings with keys to check for true and appropriate values
    :argType [args]: chain of mapping
    :returnType: any (types of values of args)

    .. code::

        yaql> switch("ab" > "abc" => 1, "ab" >= "abc" => 2, "ab" < "abc" => 3)
        3
    """
    for mapping in args:
        if mapping.source():
            return mapping.destination()


@specs.parameter('args', yaqltypes.Lambda())
def select_case(*args):
    """:yaql:selectCase

    Returns a zero-based index of the first predicate evaluated to true. If
    there is no such predicate, returns the count of arguments. All the
    predicates after the first one which was evaluated to true remain
    unevaluated.

    :signature: selectCase([args])
    :arg [args]: predicates to check for true
    :argType [args]: chain of predicates
    :returnType: integer

    .. code::

        yaql> selectCase("ab" > "abc", "ab" >= "abc", "ab" < "abc")
        2
    """
    index = 0
    for f in args:
        if f():
            return index
        index += 1
    return index


@specs.parameter('args', yaqltypes.Lambda())
def select_all_cases(*args):
    """:yaql:selectAllCases

    Evaluates input predicates and returns an iterator to collection of
    zero-based indexes of predicates which were evaluated to true. The actual
    evaluation is done lazily as the iterator advances, not during the
    function call.

    :signature: selectAllCases([args])
    :arg [args]: predicates to check for true
    :argType [args]: chain of predicates
    :returnType: iterator

    .. code::

        yaql> selectAllCases("ab" > "abc", "ab" <= "abc", "ab" < "abc")
        [1, 2]
    """
    for i, f in enumerate(args):
        if f():
            yield i


@specs.parameter('args', yaqltypes.Lambda())
def examine(*args):
    """:yaql:examine

    Evaluates predicates one by one and casts the evaluation results to
    boolean. Returns an iterator to collection of casted results. The actual
    evaluation is done lazily as the iterator advances, not during the
    function call.

    :signature: examine([args])
    :arg [args]: predicates to be evaluated
    :argType [args]: chain of predicates functions
    :returnType: iterator

    .. code::

        yaql> examine("ab" > "abc", "ab" <= "abc", "ab" < "abc")
        [false, true, true]
    """
    for f in args:
        yield bool(f())


@specs.parameter('case', int)
@specs.parameter('args', yaqltypes.Lambda())
@specs.method
def switch_case(case, *args):
    """:yaql:switchCase

    Returns evaluated `case`-th argument. If case is less than 0 or greater
    than the amount of predicates, returns evaluated last argument.
    Returns null if no args are provided.

    :signature: case.switchCase([args])
    :recieverArg case: index of predicate to be evaluated
    :argType case: integer
    :arg [args]: input predicates
    :argType [args]: chain of any types
    :returnType: any

    .. code::

        yaql> 1.switchCase('a', 1 + 1, [])
        2
        yaql> 2.switchCase('a', 1 + 1, [])
        []
        yaql> 3.switchCase('a', 1 + 1, [])
        []
        yaql> let(1) -> selectCase($ < 0, $ = 0).switchCase("less than 0",
                                                            "equal to 0",
                                                            "greater than 0")
        "greater than 0"
    """
    if 0 <= case < len(args):
        return args[case]()
    if len(args) == 0:
        return None
    return args[-1]()


@specs.parameter('args', yaqltypes.Lambda())
def coalesce(*args):
    """:yaql:coalesce

    Returns the first predicate which evaluates to non-null value. Returns null
    if no arguments are provided or if all of them are null.

    :signature: coalesce([args])
    :arg [args]: input arguments
    :argType [args]: chain of any types
    :returnType: any

    .. code::

        yaql> coalesce(null)
        null
        yaql> coalesce(null, [1, 2, 3][0], "abc")
        1
        yaql> coalesce(null, false, 1)
        false
    """
    for f in args:
        res = f()
        if res is not None:
            return res
    return None


def register(context):
    context.register_function(switch)
    context.register_function(select_case)
    context.register_function(switch_case)
    context.register_function(select_all_cases)
    context.register_function(examine)
    context.register_function(coalesce)
