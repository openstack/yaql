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
The module contains functions for regular expressions.
"""

import re

from yaql.language import specs
from yaql.language import yaqltypes

REGEX_TYPE = type(re.compile('.'))


@specs.parameter('pattern', yaqltypes.String())
def regex(pattern, ignore_case=False, multi_line=False, dot_all=False):
    """:yaql:regex

    Returns regular expression object with provided flags. Can be used for
    matching using matches method.

    :signature: regex(pattern,ignoreCase => false, multiLine => false,
        dotAll => false)
    :arg pattern: regular expression pattern to be compiled to regex object
    :argType pattern: string
    :arg ignoreCase: true makes performing case-insensitive matching.
    :argType ignoreCase: boolean
    :arg multiLine: true makes character '^' to match at the beginning of the
        string and at the beginning of each line, the character '$' to match
        at the end of the string and at the end of each line. false means
        '^' to match only at the beginning of the string, '$' only at the end
        of the string.
    :argType multiLine: boolean
    :arg dotAll: true makes the '.' special character to match any character
        (including a newline). false makes '.' to match anything except
        a newline.
    :argType dotAll: boolean
    :returnType: regex object

    .. code::

        yaql> regex("a.c").matches("abc")
        true
        yaql> regex("A.c").matches("abc")
        false
        yaql> regex("A.c", ignoreCase => true).matches("abc")
        true
    """
    flags = re.UNICODE
    if ignore_case:
        flags |= re.IGNORECASE
    if multi_line:
        flags |= re.MULTILINE
    if dot_all:
        flags |= re.DOTALL
    return re.compile(pattern, flags)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.method
def matches(regexp, string):
    """:yaql:matches

    Returns true if string matches regexp.

    :signature: regexp.matches(string)
    :receiverArg regexp: regex pattern
    :argType regexp: regex object
    :arg string: string to find match in
    :argType string: string
    :returnType: boolean

    .. code::

        yaql> regex("a.c").matches("abc")
        true
    """
    return regexp.search(string) is not None


@specs.parameter('string', yaqltypes.String())
@specs.parameter('regexp', yaqltypes.String())
@specs.method
def matches_(string, regexp):
    """:yaql:matches

    Returns true if string matches regexp, false otherwise.

    :signature: string.matches(regexp)
    :receiverArg string: string to find match in
    :argType string: string
    :arg regexp: regex pattern
    :argType regexp: regex object
    :returnType: boolean

    .. code::

        yaql> "abc".matches("a.c")
        true
    """
    return re.search(regexp, string) is not None


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.name('#operator_=~')
def matches_operator_regex(string, regexp):
    """:yaql:operator =~

    Returns true if left matches right, false otherwise.

    :signature: left =~ right
    :arg left: string to find match in
    :argType left: string
    :arg right: regex pattern
    :argType right: regex
    :returnType: boolean

    .. code::

        yaql> "abc" =~ regex("a.c")
        true
    """
    return regexp.search(string) is not None


@specs.parameter('pattern', yaqltypes.String())
@specs.parameter('string', yaqltypes.String())
@specs.name('#operator_=~')
def matches_operator_string(string, pattern):
    """:yaql:operator =~

    Returns true if left matches right, false otherwise.

    :signature: left =~ right
    :arg left: string to find match in
    :argType left: string
    :arg right: regex pattern
    :argType right: string
    :returnType: boolean

    .. code::

        yaql> "abc" =~ "a.c"
        true
    """
    return re.search(pattern, string) is not None


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.name('#operator_!~')
def not_matches_operator_regex(string, regexp):
    """:yaql:operator !~

    Returns true if left doesn't match right, false otherwise.

    :signature: left !~ right
    :arg left: string to find match in
    :argType left: string
    :arg right: regex pattern
    :argType right: regex
    :returnType: boolean

    .. code::

        yaql> "acb" !~ regex("a.c")
        true
        yaql> "abc" !~ regex("a.c")
        false
    """
    return regexp.search(string) is None


@specs.parameter('pattern', yaqltypes.String())
@specs.parameter('string', yaqltypes.String())
@specs.name('#operator_!~')
def not_matches_operator_string(string, pattern):
    """:yaql:operator !~

    Returns true if left doesn't match right, false otherwise.

    :signature: left !~ right
    :arg left: string to find match in
    :argType left: string
    :arg right: regex pattern
    :argType right: regex object
    :returnType: boolean

    .. code::

        yaql> "acb" !~ regex("a.c")
        true
        yaql> "abc" !~ regex("a.c")
        false
    """
    return re.search(pattern, string) is None


def _publish_match(context, match):
    rec = {
        'value': match.group(),
        'start': match.start(0),
        'end': match.end(0)
    }
    context['$1'] = rec
    for i, t in enumerate(match.groups(), 1):
        rec = {
            'value': t,
            'start': match.start(i),
            'end': match.end(i)
        }
        context['$' + str(i + 1)] = rec

    for key, value, in match.groupdict().values():
        rec = {
            'value': value,
            'start': match.start(value),
            'end': match.end(value)
        }
        context['$' + key] = rec


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('selector', yaqltypes.Lambda(with_context=True))
@specs.method
def search(context, regexp, string, selector=None):
    """:yaql:search

    Search substring which matches regexp. Returns selector applied to
    dictionary {"start" => ..., "end" => ..., "value" => ...} where appropriate
    values describe start of substring, its end and itself. By default, if no
    selector is specified, returns only substring.
    null is a return value if there is no substring which matches regexp.

    :signature: regexp.search(string, selector => null)
    :receiverArg regexp: regex pattern
    :argType regexp: regex object
    :arg string: string to find match in
    :argType string: string
    :arg selector: lambda function to be applied to resulted dictionary with
        keys 'start', 'end', 'value'. null by default, which means to return
        only substring.
    :argType selector: lambda
    :returnType: string or selector return type

    .. code::

        yaql> regex("a.c").search("abcabc")
        "abc"
        yaql> regex("a.c").search("cabc", $)
        {
            "start": 1,
            "end": 4,
            "value": "abc"
        }
        yaql> regex("a.c").search("cabc", $.start)
        1
    """
    res = regexp.search(string)
    new_context = context.create_child_context()
    if res is None:
        return None
    if selector is None:
        return res.group()
    _publish_match(new_context, res)
    return selector(new_context)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('selector', yaqltypes.Lambda(with_context=True))
@specs.method
def search_all(context, regexp, string, selector=None):
    """:yaql:searchAll

    Search all substrings which matches regexp. Returns list of applied to
    dictionary {"start" => ..., "end" => ..., "value" => ...} selector, where
    appropriate values describe start of every substring, its end and itself.
    By default, if no selector is specified, returns only list of substrings.

    :signature: regexp.searchAll(string, selector => null)
    :receiverArg regexp: regex pattern
    :argType regexp: regex object
    :arg string: string to find match in
    :argType string: string
    :arg selector: lambda function to be applied to resulted dictionary of
        every substring with keys 'start', 'end', 'value'. null by default,
        which means to return only list of substrings.
    :argType selector: lambda
    :returnType: list

    .. code::

        yaql> regex("a.c").searchAll("abcadc")
        ["abc", "adc"]
        yaql> regex("a.c").searchAll("abcadc", $)
        [
            {
                "start": 0,
                "end": 3,
                "value": "abc"
            },
            {
                "start": 3,
                "end": 6,
                "value": "adc"
            }
        ]

    :name: searchAll
    """
    for res in regexp.finditer(string):
        new_context = context.create_child_context()
        if selector is None:
            yield res.group()
        else:
            _publish_match(new_context, res)
            yield selector(new_context)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('max_split', int)
@specs.method
def split(regexp, string, max_split=0):
    """:yaql:split

    Splits string by regexp matches and returns list of strings.

    :signature: regexp.split(string, maxSplit => 0)
    :receiverArg regexp: regex pattern
    :argType regexp: regex object
    :arg string: string to be splitted
    :argType string: string
    :arg maxSplit: how many first splits to do. 0 by default, which means
        to split by all matches
    :argType maxSplit: integer
    :returnType: list

    .. code::

        yaql> regex("a.").split("abcadc")
        ["", "c", "c"]
        yaql> regex("a.").split("abcadc", maxSplit => 1)
        ["", "cadc"]
    """
    return regexp.split(string, max_split)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('max_split', int)
@specs.method
@specs.name('split')
def split_string(string, regexp, max_split=0):
    """:yaql:split

    Splits string by regexp matches and returns list of strings.

    :signature: string.split(regexp, maxSplit => 0)
    :receiverArg string: string to be splitted
    :argType string: string
    :arg regexp: regex pattern
    :argType regexp: regex object
    :arg maxSplit: how many first splits to do. 0 by default, which means
        to split by all matches
    :argType maxSplit: integer
    :returnType: list

    .. code::

        yaql> "abcadc".split(regex("a."))
        ["", "c", "c"]
        yaql> "abcadc".split(regex("a."), maxSplit => 1)
        ["", "cadc"]
    """
    return regexp.split(string, max_split)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('repl', yaqltypes.String())
@specs.parameter('count', int)
@specs.method
def replace(regexp, string, repl, count=0):
    """:yaql:replace

    Returns the string obtained by replacing the leftmost non-overlapping
    matches of regexp in string by the replacement repl, where the latter is
    only string-type.

    :signature: regexp.replace(string, repl, count => 0)
    :receiverArg regexp: regex pattern
    :argType regexp: regex object
    :arg string: string to make replace in
    :argType string: string
    :arg repl: string to replace matches of regexp
    :argType repl: string
    :arg count: how many first replaces to do. 0 by default, which means
        to do all replacements
    :argType count: integer
    :returnType: string

    .. code::

        yaql> regex("a.").replace("abcadc", "xx")
        "xxcxxc"
        yaql> regex("a.").replace("abcadc", "xx", count => 1)
        "xxcadc"
    """
    return regexp.sub(repl, string, count)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('repl', yaqltypes.String())
@specs.parameter('count', int)
@specs.method
@specs.name('replace')
def replace_string(string, regexp, repl, count=0):
    """:yaql:replace

    Returns the string obtained by replacing the leftmost non-overlapping
    matches of regexp in string by the replacement repl, where the latter is
    only string-type.

    :signature: string.replace(regexp, repl, count => 0)
    :receiverArg string: string to make replace in
    :argType string: string
    :arg regexp: regex pattern
    :argType regexp: regex object
    :arg repl: string to replace matches of regexp
    :argType repl: string
    :arg count: how many first replaces to do. 0 by default, which means
        to do all replacements
    :argType count: integer
    :returnType: string

    .. code::

        yaql> "abcadc".replace(regex("a."), "xx")
        "xxcxxc"
    """
    return replace(regexp, string, repl, count)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('repl', yaqltypes.Lambda(with_context=True))
@specs.parameter('count', int)
@specs.method
def replace_by(context, regexp, string, repl, count=0):
    """:yaql:replaceBy

    Returns the string obtained by replacing the leftmost non-overlapping
    matches of regexp in string by repl, where the latter is an expression to
    get replacements by obtained matches.

    :signature: regexp.replaceBy(string, repl, count => 0)
    :receiverArg regexp: regex pattern
    :argType regexp: regex object
    :arg string: string to make replace in
    :argType string: string
    :arg repl: lambda function which returns string to make replacements
        according to input matches
    :argType repl: lambda
    :arg count: how many first replaces to do. 0 by default, which means
        to do all replacements
    :argType count: integer
    :returnType: string

    .. code::

        yaql> regex("a.c").replaceBy("abcadc", switch($.value = "abc" => xx,
                                                      $.value = "adc" => yy))
        "xxyy"
    """
    def repl_func(match):
        new_context = context.create_child_context()
        _publish_match(context, match)
        return repl(new_context)
    return regexp.sub(repl_func, string, count)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('repl', yaqltypes.Lambda(with_context=True))
@specs.parameter('count', int)
@specs.method
@specs.name('replaceBy')
def replace_by_string(context, string, regexp, repl, count=0):
    """:yaql:replaceBy

    Replaces matches of regexp in string with values provided by the
    supplied function.

    :signature: string.replaceBy(regexp, repl, count => 0)
    :receiverArg string: string to make replace in
    :argType string: string
    :arg regexp: regex pattern
    :argType regexp: regex object
    :arg repl: lambda function which returns string to make replacements
        according to input matches
    :argType repl: lambda
    :arg count: how many first replaces to do. 0 by default, which means
        to do all replacements
    :argType count: integer
    :returnType: string

    .. code::

        yaql> "abcadc".replaceBy(regex("a.c"), switch($.value = "abc" => xx,
                                                      $.value = "adc" => yy))
        "xxyy"
    """
    return replace_by(context, regexp, string, repl, count)


@specs.parameter('string', yaqltypes.String())
def escape_regex(string):
    """:yaql:escapeRegex

    Returns string with all the characters except ASCII letters, numbers,
    and '_' escaped.

    :signature: escapeRegex(string)
    :arg string: string to backslash all non-alphanumerics
    :argType string: string
    :returnType: string

    .. code::

        yaql> escapeRegex('a.')
        "a\\."
    """
    return re.escape(string)


def is_regex(value):
    """:yaql:isRegex

    Returns true if value is a regex object.

    :signature: isRegex(value)
    :arg value: string to backslash all non-alphanumerics
    :argType value: any
    :returnType: boolean

    .. code::

        yaql> isRegex(regex("a.c"))
        true
        yaql> isRegex(regex("a.c").matches("abc"))
        false
    """
    return isinstance(value, REGEX_TYPE)


def register(context):
    context.register_function(regex)
    context.register_function(matches)
    context.register_function(matches_)
    context.register_function(matches_operator_string)
    context.register_function(matches_operator_regex)
    context.register_function(not_matches_operator_string)
    context.register_function(not_matches_operator_regex)
    context.register_function(search)
    context.register_function(search_all)
    context.register_function(split)
    context.register_function(split_string)
    context.register_function(replace)
    context.register_function(replace_by)
    context.register_function(replace_string)
    context.register_function(replace_by_string)
    context.register_function(escape_regex)
    context.register_function(is_regex)
