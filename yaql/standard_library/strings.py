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
The module describes which operations can be done with strings in YAQL.
"""

import string as string_module

import six

from yaql.language import specs
from yaql.language import utils
from yaql.language import yaqltypes


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_>')
def gt(left, right):
    """:yaql:operator >

    Returns true if the left operand is strictly greater than the right,
    ordering lexicographically, otherwise false.

    :signature: left > right
    :arg left: left operand
    :argType left: string
    :arg right: right operand
    :argType right: string
    :returnType: boolean

    .. code::

        yaql> "abc" > "ab"
        true
        yaql> "abc" > "abb"
        true
        yaql> "abc" > "abc"
        false
    """
    return left > right


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_<')
def lt(left, right):
    """:yaql:operator <

    Returns true if the left operand is strictly less than the right, ordering
    lexicographically, otherwise false.

    :signature: left < right
    :arg left: left operand
    :argType left: string
    :arg right: right operand
    :argType right: string
    :returnType: boolean

    .. code::

        yaql> "ab" < "abc"
        true
        yaql> "abb" < "abc"
        true
        yaql> "abc" < "abc"
        false
    """
    return left < right


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_>=')
def gte(left, right):
    """:yaql:operator >=

    Returns true if the left operand is greater or equal to the right, ordering
    lexicographically, otherwise false.

    :signature: left >= right
    :arg left: left operand
    :argType left: string
    :arg right: right operand
    :argType right: string
    :returnType: boolean

    .. code::

        yaql> "abc" >= "ab"
        true
        yaql> "abc" >= "abc"
        true
    """
    return left >= right


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_<=')
def lte(left, right):
    """:yaql:operator <=

    Returns true if the left operand is less or equal to the right, ordering
    lexicographically, otherwise false.

    :signature: left <= right
    :arg left: left operand
    :argType left: string
    :arg right: right operand
    :argType right: string
    :returnType: boolean

    .. code::

        yaql> "ab" <= "abc"
        true
        yaql> "abc" <= "abc"
        true
    """
    return left <= right


@specs.parameter('args', yaqltypes.String())
def concat(*args):
    """:yaql:concat

    Returns concatenated args.

    :signature: concat([args])
    :arg [args]: values to be joined
    :argType [args]: string
    :returnType: string

    .. code::

        yaql> concat("abc", "de", "f")
        "abcdef"
    """
    return ''.join(args)


@specs.parameter('string', yaqltypes.String())
@specs.method
def to_upper(string):
    """:yaql:toUpper

    Returns a string with all case-based characters uppercase.

    :signature: string.toUpper()
    :receiverArg string: value to uppercase
    :argType string: string
    :returnType: string

    .. code::

        yaql> "aB1c".toUpper()
        "AB1C"
    """
    return string.upper()


@specs.parameter('string', yaqltypes.String())
@specs.extension_method
def len_(string):
    """:yaql:len

    Returns size of the string.

    :signature: string.len()
    :receiverArg string: input string
    :argType string: string
    :returnType: integer

    .. code::

        yaql> "abc".len()
        3
    """
    return len(string)


@specs.parameter('string', yaqltypes.String())
@specs.method
def to_lower(string):
    """:yaql:toLower

    Returns a string with all case-based characters lowercase.

    :signature: string.toLower()
    :receiverArg string: value to lowercase
    :argType string: string
    :returnType: string

    .. code::

        yaql> "AB1c".toLower()
        "ab1c"
    """
    return string.lower()


@specs.parameter('string', yaqltypes.String())
@specs.parameter('separator', yaqltypes.String(nullable=True))
@specs.parameter('max_splits', int)
@specs.method
def split(string, separator=None, max_splits=-1):
    """:yaql:split

    Returns a list of tokens in the string, using separator as the
    delimiter.

    :signature: string.split(separator => null, maxSplits => -1)
    :receiverArg string: value to be splitted
    :argType string: string
    :arg separator: delimiter for splitting. null by default, which means
        splitting with whitespace characters
    :argType separator: string
    :arg maxSplits: maximum number of splittings. -1 by default, which means
        all possible splits are done
    :argType maxSplits: integer
    :returnType: list

    .. code::

        yaql> "abc     de  f".split()
        ["abc", "de", "f"]
        yaql> "abc     de  f".split(maxSplits => 1)
        ["abc", "de  f"]
        yaql> "abcde".split("c")
        ["ab", "de"]
    """
    return string.split(separator, max_splits)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('separator', yaqltypes.String(nullable=True))
@specs.parameter('max_splits', int)
@specs.method
def right_split(string, separator=None, max_splits=-1):
    """:yaql:rightSplit

    Returns a list of tokens in the string, using separator as the
    delimiter. If maxSplits is given then at most maxSplits splits are done -
    the rightmost ones.

    :signature: string.rightSplit(separator => null, maxSplits => -1)
    :receiverArg string: value to be splitted
    :argType string: string
    :arg separator: delimiter for splitting. null by default, which means
        splitting with whitespace characters
    :argType separator: string
    :arg maxSplits: number of splits to be done - the rightmost ones.
        -1 by default, which means all possible splits are done
    :argType maxSplits: integer
    :returnType: list

    .. code::

        yaql> "abc     de  f".rightSplit()
        ["abc", "de", "f"]
        yaql> "abc     de  f".rightSplit(maxSplits => 1)
        ["abc     de", "f"]
    """
    return string.rsplit(separator, max_splits)


@specs.parameter('sequence', yaqltypes.Iterable())
@specs.parameter('separator', yaqltypes.String())
@specs.inject('str_delegate', yaqltypes.Delegate('str'))
@specs.method
def join(sequence, separator, str_delegate):
    """:yaql:join

    Returns a string with sequence elements joined by the separator.

    :signature: sequence.join(separator)
    :receiverArg sequence: chain of values to be joined
    :argType sequence: sequence of strings
    :arg separator: value to be placed between joined pairs
    :argType separator: string
    :returnType: string

    .. code::

        yaql> ["abc", "de", "f"].join("")
        "abcdef"
        yaql> ["abc", "de", "f"].join("|")
        "abc|de|f"
    """
    return separator.join(six.moves.map(str_delegate, sequence))


@specs.parameter('sequence', yaqltypes.Iterable())
@specs.parameter('separator', yaqltypes.String())
@specs.inject('str_delegate', yaqltypes.Delegate('str'))
@specs.method
def join_(separator, sequence, str_delegate):
    """:yaql:join

    Returns a string with sequence elements joined by the separator.

    :signature: separator.join(sequence)
    :receiverArg separator: value to be placed between joined pairs
    :argType separator: string
    :arg sequence: chain of values to be joined
    :argType sequence: sequence of strings
    :returnType: string

    .. code::

        yaql> "|".join(["abc", "de", "f"])
        "abc|de|f"
    """
    return join(sequence, separator, str_delegate)


@specs.parameter('value', nullable=True)
def str_(value):
    """:yaql:str

    Returns a string representation of the value.

    :signature: str(value)
    :arg value: value to be evaluated to string
    :argType value: any
    :returnType: string

    .. code::

        yaql> str(["abc", "de"])
        "(u'abc', u'd')"
        yaql> str(123)
        "123"
    """
    if value is None:
        return 'null'
    elif value is True:
        return 'true'
    elif value is False:
        return 'false'
    else:
        return six.text_type(value)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('chars', yaqltypes.String(nullable=True))
@specs.method
def trim(string, chars=None):
    """:yaql:trim

    Returns a string with the leading and trailing chars removed.

    :signature: string.trim(chars => null)
    :receiverArg string: value to be trimmed
    :argType string: string
    :arg chars: symbols to be removed from input string. null by default,
        which means trim is done with whitespace characters
    :argType chars: string
    :returnType: string

    .. code::

        yaql> "  abcd ".trim()
        "abcd"
        yaql> "aababa".trim("a")
        "bab"
    """
    return string.strip(chars)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('chars', yaqltypes.String(nullable=True))
@specs.method
def trim_left(string, chars=None):
    """:yaql:trimLeft

    Returns a string with the leading chars removed.

    :signature: string.trimLeft(chars => null)
    :receiverArg string: value to be trimmed
    :argType string: string
    :arg chars: symbols to be removed from start of input string. null by
        default, which means trim is done with whitespace characters
    :argType chars: string
    :returnType: string

    .. code::

        yaql> "  abcd ".trimLeft()
        "abcd "
        yaql> "aababa".trimLeft("a")
        "baba"
    """
    return string.lstrip(chars)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('chars', yaqltypes.String(nullable=True))
@specs.method
def trim_right(string, chars=None):
    """:yaql:trimRight

    Returns a string with the trailing chars removed.

    :signature: string.trimRight(chars => null)
    :receiverArg string: value to be trimmed
    :argType string: string
    :arg chars: symbols to be removed from end of input string. null by
        default, which means trim is done with whitespace characters
    :argType chars: string
    :returnType: string

    .. code::

        yaql> "  abcd ".trimRight()
        "  abcd"
        yaql> "aababa".trimRight("a")
        "aabab"
    """
    return string.rstrip(chars)


@specs.parameter('string', yaqltypes.String(nullable=True))
@specs.parameter('chars', yaqltypes.String(nullable=True))
@specs.extension_method
def norm(string, chars=None):
    """:yaql:norm

    Returns a string with the leading and trailing chars removed.
    If the resulting string is empty, returns null.

    :signature: string.norm(chars => null)
    :receiverArg string: value to be cut with specified chars
    :argType string: string
    :arg chars: symbols to be removed from the start and the end of input
        string. null by default, which means norm is done with whitespace
        characters
    :argType chars: string
    :returnType: string

    .. code::

        yaql> "  abcd ".norm()
        "abcd"
        yaql> "aaaa".norm("a")
        null
    """
    if string is None:
        return None
    value = string.strip(chars)
    return None if not value else value


@specs.parameter('string', yaqltypes.String(nullable=True))
@specs.parameter('trim_spaces', bool, alias='trim')
@specs.parameter('chars', yaqltypes.String(nullable=True))
@specs.extension_method
def is_empty(string, trim_spaces=True, chars=None):
    """:yaql:isEmpty

    Returns true if the string with removed leading and trailing chars is
    empty.

    :signature: string.isEmpty(trimSpaces => true, chars => null)
    :receiverArg string: value to be checked for emptiness after trim
    :argType string: string
    :arg trimSpaces: true by default, which means string to be trimmed with
        chars. false means checking whether input string is empty
    :argType trimSpaces: boolean
    :arg chars: symbols for trimming. null by default, which means trim is
        done with whitespace characters
    :argType chars: string
    :returnType: boolean

    .. code::

        yaql> "abaab".isEmpty(chars=>"ab")
        true
        yaql> "aba".isEmpty(chars=>"a")
        false
    """
    if string is None:
        return True
    if trim_spaces:
        string = string.strip(chars)
    return not string


@specs.parameter('string', yaqltypes.String())
@specs.parameter('old', yaqltypes.String())
@specs.parameter('new', yaqltypes.String())
@specs.parameter('count', int)
@specs.method
def replace(string, old, new, count=-1):
    """:yaql:replace

    Returns a string with first count occurrences of old replaced with new.

    :signature: string.replace(old, new, count => -1)
    :receiverArg string: input string
    :argType string: string
    :arg old: value to be replaced
    :argType old: string
    :arg new: replacement for old value
    :argType new: string
    :arg count: how many first replacements to do. -1 by default, which means
        to do all replacements
    :argType count: integer
    :returnType: string

    .. code::

        yaql> "abaab".replace("ab", "cd")
        "cdacd"
    """
    return string.replace(old, new, count)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('replacements', utils.MappingType)
@specs.parameter('count', int)
@specs.inject('str_func', yaqltypes.Delegate('str'))
@specs.method
@specs.name('replace')
def replace_with_dict(string, str_func, replacements, count=-1):
    """:yaql:replace

    Returns a string with all occurrences of replacements' keys replaced
    with corresponding replacements' values.
    If count is specified, only the first count occurrences of every key
    are replaced.

    :signature: string.replace(replacements, count => -1)
    :receiverArg string: input string
    :argType string: string
    :arg replacements: dict of replacements in format {old => new ...}
    :argType replacements: mapping
    :arg count: how many first occurrences of every key are replaced. -1 by
        default, which means to do all replacements
    :argType count: integer
    :returnType: string

    .. code::

        yaql> "abc ab abc".replace({abc => xx, ab => yy})
        "xx yy xx"
        yaql> "abc ab abc".replace({ab => yy, abc => xx})
        "yyc yy yyc"
        yaql> "abc ab abc".replace({ab => yy, abc => xx}, 1)
        "yyc ab xx"
    """
    for key, value in six.iteritems(replacements):
        string = string.replace(str_func(key), str_func(value), count)
    return string


@specs.parameter('__format_string', yaqltypes.String())
@specs.extension_method
def format_(__format_string, *args, **kwargs):
    """:yaql:format

    Returns a string formatted with positional and keyword arguments.

    :signature: string.format([args], {kwargs})
    :receiverArg string: input string for formatting. Can be passed only as
        first positional argument if used as a function. Can contain literal
        text or replacement fields marked by braces {}. Every replacement field
        should contain either the numeric index of a positional argument or the
        name of a keyword argument
    :argType string: string
    :arg [args]: values for replacements for numeric markers
    :argType [args]: chain of strings
    :arg {kwargs}: values for keyword replacements
    :argType {kwargs}: chain of key-value arguments, where values are strings
    :returnValue: string

    .. code::

        yaql> "abc{0}ab{1}abc".format(" ", ",")
        "abc ab,abc"
        yaql> "abc{foo}ab{bar}abc".format(foo => " ", bar => ",")
        "abc ab,abc"
        yaql> format("abc{0}ab{foo}abc", ' ', foo => ",")
        "abc ab,abc"
    """
    return __format_string.format(*args, **kwargs)


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', int)
@specs.name('#operator_*')
def string_by_int(left, right, engine):
    """:yaql:operator *

    Returns string repeated count times.

    :signature: left * right
    :arg left: left operand
    :argType left: string
    :arg right: right operator, how many times repeat input string
    :argType right: integer
    :returnType: string

    .. code::

        yaql> "ab" * 2
        "abab"
    """
    utils.limit_memory_usage(engine, (-right + 1, u''), (right, left))
    return left * right


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_in')
def in_(left, right):
    """:yaql:operator in

    Returns true if there is at least one occurrence of left string in right.

    :signature: left in right
    :arg left: left operand, which occurrence is checked
    :argType left: string
    :arg right: right operand
    :argType right: string
    :returnType: boolean

    .. code::

        yaql> "ab" in "abc"
        true
        yaql> "ab" in "acb"
        false
    """
    return left in right


@specs.parameter('left', int)
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_*')
def int_by_string(left, right, engine):
    """:yaql:operator *

    Returns string repeated count times.

    :signature: left * right
    :arg left: left operand, how many times repeat input string
    :argType left: integer
    :arg right: right operator
    :argType right: string
    :returnType: string

    .. code::

        yaql> 2 * "ab"
        "abab"
    """
    return string_by_int(right, left, engine)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('start', int)
@specs.parameter('length', int)
@specs.method
def substring(string, start, length=-1):
    """:yaql:substring

    Returns a substring beginning from start index ending with start+end index.

    :signature: string.substring(start, length => -1)
    :receiverArg string: input string
    :argType string: string
    :arg start: index for substring to start with
    :argType start: integer
    :arg length: length of substring. -1 by default, which means end of
        substring to be equal to the end of input string
    :argType length: integer
    :returnType: string

    .. code::

        yaql> "abcd".substring(1)
        "bcd"
        yaql> "abcd".substring(1, 2)
        "bc"
    """
    if length < 0:
        length = len(string)
    if start < 0:
        start += len(string)
    return string[start:start + length]


@specs.parameter('string', yaqltypes.String())
@specs.parameter('sub', yaqltypes.String())
@specs.parameter('start', int)
@specs.method
def index_of(string, sub, start=0):
    """:yaql:indexOf

    Returns an index of first occurrence sub in string beginning from start.
    -1 is a return value if there is no any occurrence.

    :signature: string.indexOf(sub, start => 0)
    :receiverArg string: input string
    :argType string: string
    :arg sub: substring to find in string
    :argType sub: string
    :arg start: index to start search with, 0 by default
    :argType start: integer
    :returnType: integer

    .. code::

        yaql> "cabcdab".indexOf("ab")
        1
        yaql> "cabcdab".indexOf("ab", 2)
        5
        yaql> "cabcdab".indexOf("ab", 6)
        -1
    """
    return string.find(sub, start)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('sub', yaqltypes.String())
@specs.parameter('start', int)
@specs.parameter('length', int)
@specs.method
def index_of_(string, sub, start, length):
    """:yaql:indexOf

    Returns an index of first occurrence sub in string beginning from start
    ending with start+length.
    -1 is a return value if there is no any occurrence.

    :signature: string.indexOf(sub, start, length)
    :receiverArg string: input string
    :argType string: string
    :arg sub: substring to find in string
    :argType sub: string
    :arg start: index to start search with, 0 by default
    :argType start: integer
    :arg length: length of string to find substring in
    :argType length: integer
    :returnType: integer

    .. code::

        yaql> "cabcdab".indexOf("bc", 2, 2)
        2
    """
    if start < 0:
        start += len(string)
    if length < 0:
        length = len(string) - start
    return string.find(sub, start, start + length)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('sub', yaqltypes.String())
@specs.parameter('start', int)
@specs.method
def last_index_of(string, sub, start=0):
    """:yaql:lastIndexOf

    Returns an index of last occurrence sub in string beginning from start.
    -1 is a return value if there is no any occurrence.

    :signature: string.lastIndexOf(sub, start => 0)
    :receiverArg string: input string
    :argType string: string
    :arg sub: substring to find in string
    :argType sub: string
    :arg start: index to start search with, 0 by default
    :argType start: integer
    :returnType: integer

    .. code::

        yaql> "cabcdab".lastIndexOf("ab")
        5
    """
    return string.rfind(sub, start)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('sub', yaqltypes.String())
@specs.parameter('start', int)
@specs.parameter('length', int)
@specs.method
def last_index_of_(string, sub, start, length):
    """:yaql:lastIndexOf

    Returns an index of last occurrence sub in string beginning from start
    ending with start+length.
    -1 is a return value if there is no any occurrence.

    :signature: string.lastIndexOf(sub, start, length)
    :receiverArg string: input string
    :argType string: string
    :arg sub: substring to find in string
    :argType sub: string
    :arg start: index to start search with, 0 by default
    :argType start: integer
    :arg length: length of string to find substring in
    :argType length: integer
    :returnType: integer

    .. code::

        yaql> "cabcdbc".lastIndexOf("bc", 2, 5)
        5
    """
    if start < 0:
        start += len(string)
    if length < 0:
        length = len(string) - start
    return string.rfind(sub, start, start + length)


@specs.parameter('string', yaqltypes.String())
@specs.method
def to_char_array(string):
    """:yaql:toCharArray

    Converts a string to array of one character strings.

    :signature: string.toCharArray()
    :receiverArg string: input string
    :argType string: string
    :returnType: list

    .. code::

        yaql> "abc de".toCharArray()
        ["a", "b", "c", " ", "d", "e"]
    """
    return tuple(string)


def characters(
        digits=False, hexdigits=False,
        ascii_lowercase=False, ascii_uppercase=False,
        ascii_letters=False, letters=False,
        octdigits=False, punctuation=False, printable=False,
        lowercase=False, uppercase=False, whitespace=False):
    """:yaql:characters

    Returns a list of all distinct items of specified types.

    :signature: characters(digits => false, hexdigits => false,
                           asciiLowercase => false, asciiUppercase => false,
                           asciiLetters => false, letters => false,
                           octdigits => false, punctuation => false,
                           printable => false, lowercase => false,
                           uppercase => false, whitespace => false)
    :arg digits: include digits in output list if true, false by default
    :argType digits: boolean
    :arg hexdigits: include hexademical digits in output list if true, false
        by default
    :argType hexdigits: boolean
    :arg asciiLowercase: include ASCII lowercase letters in output list if
        true, false by default
    :argType asciiLowercase: boolean
    :arg asciiUppercase: include ASCII uppercase letters in output list if
        true, false by default
    :argType asciiUppercase: boolean
    :arg asciiLetters: include both ASCII lowercase and uppercase letters
        in output list if true, false by default
    :argType asciiLetters: boolean
    :arg letters: include both lowercase and uppercase letters in output list
        if true, false by default
    :argType letters: boolean
    :arg octdigits: include digits from 0 to 7 in output list if true, false
        by default
    :argType octdigits: boolean
    :arg punctuation: include ASCII characters, which are considered
        punctuation, in output list if true, false by default
    :argType punctuation: boolean
    :arg printable: include digits, letters, punctuation, and whitespace in
        output list if true, false by default
    :argType printable: boolean
    :arg lowercase: include lowercase letters in output list if true, false
        by default
    :argType lowercase: boolean
    :arg uppercase: include uppercase letters in output list if true, false
        by default
    :argType uppercase: boolean
    :arg whitespace: include all characters that are considered whitespace
        in output list if true, false by default
    :argType whitespace: boolean
    :returnType: list

    .. code::

        yaql> characters(digits => true)
        ["1", "0", "3", "2", "5", "4", "7", "6", "9", "8"]

    """
    string = ''
    if digits:
        string += string_module.digits
    if hexdigits:
        string += string_module.hexdigits
    if ascii_lowercase:
        string += string_module.ascii_lowercase
    if ascii_uppercase:
        string += string_module.ascii_uppercase
    if ascii_letters:
        string += string_module.ascii_letters
    if letters:
        string += string_module.letters
    if octdigits:
        string += string_module.octdigits
    if punctuation:
        string += string_module.punctuation
    if printable:
        string += string_module.printable
    if lowercase:
        string += string_module.lowercase
    if uppercase:
        string += string_module.uppercase
    if whitespace:
        string += string_module.whitespace
    return tuple(set(string))


def is_string(arg):
    """:yaql:isString

    Returns true if arg is a string.

    :signature: isString(arg)
    :arg arg: input value
    :argType arg: any
    :returnType: boolean

    .. code::

        yaql> isString("ab")
        true
        yaql> isString(1)
        false
    """
    return isinstance(arg, six.string_types)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('prefixes', yaqltypes.String())
@specs.method
def starts_with(string, *prefixes):
    """:yaql:startsWith

    Returns true if a string starts with any of given args.

    :signature: string.startsWith([args])
    :receiverArg string: input string
    :argType string: string
    :arg [args]: chain of strings to check input string with
    :argType [args]: strings
    :returnType: boolean

    .. code::

        yaql> "abcd".startsWith("ab", "xx")
        true
        yaql> "abcd".startsWith("yy", "xx", "zz")
        false
    """
    return string.startswith(prefixes)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('suffixes', yaqltypes.String())
@specs.method
def ends_with(string, *suffixes):
    """:yaql:endsWith

    Returns true if a string ends with any of given args.

    :signature: string.endsWith([args])
    :receiverArg string: input string
    :argType string: string
    :arg [args]: chain of strings to check input string with
    :argType [args]: strings
    :returnType: boolean

    .. code::

        yaql> "abcd".endsWith("cd", "xx")
        true
        yaql> "abcd".endsWith("yy", "xx", "zz")
        false
    """
    return string.endswith(suffixes)


@specs.parameter('num', yaqltypes.Number(nullable=True))
def hex_(num):
    """:yaql:hex

    Returns a string with hexadecimal representation of num.

    :signature: hex(num)
    :arg num: input number to be converted to hexademical
    :argType num: number
    :returnType: string

    .. code::

        yaql> hex(256)
        "0x100"
    """
    return hex(num)


def register(context):
    context.register_function(gt)
    context.register_function(lt)
    context.register_function(gte)
    context.register_function(lte)
    context.register_function(len_)
    context.register_function(to_lower)
    context.register_function(to_upper)
    context.register_function(split)
    context.register_function(right_split)
    context.register_function(join)
    context.register_function(join_)
    context.register_function(str_)
    context.register_function(concat)
    context.register_function(concat, name='#operator_+')
    context.register_function(trim)
    context.register_function(trim_left)
    context.register_function(trim_right)
    context.register_function(replace)
    context.register_function(replace_with_dict)
    context.register_function(format_)
    context.register_function(is_empty)
    context.register_function(string_by_int)
    context.register_function(int_by_string)
    context.register_function(substring)
    context.register_function(index_of)
    context.register_function(index_of_)
    context.register_function(last_index_of)
    context.register_function(last_index_of_)
    context.register_function(to_char_array)
    context.register_function(characters)
    context.register_function(is_string)
    context.register_function(norm)
    context.register_function(in_)
    context.register_function(starts_with)
    context.register_function(ends_with)
    context.register_function(hex_)
