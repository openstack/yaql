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

import string as string_module

import six

from yaql.language import specs
from yaql.language import utils
from yaql.language import yaqltypes


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_>')
def gt(left, right):
    return left > right


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_<')
def lt(left, right):
    return left < right


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_>=')
def gte(left, right):
    return left > right


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_<=')
def lte(left, right):
    return left < right


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('*equal')
def eq(left, right):
    return left == right


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('*not_equal')
def neq(left, right):
    return left != right


@specs.parameter('args', yaqltypes.String())
def concat(*args):
    return ''.join(args)


@specs.parameter('string', yaqltypes.String())
@specs.method
def to_upper(string):
    return string.upper()


@specs.parameter('string', yaqltypes.String())
@specs.extension_method
def len_(string):
    return len(string)


@specs.parameter('string', yaqltypes.String())
@specs.method
def to_lower(string):
    return string.lower()


@specs.parameter('string', yaqltypes.String())
@specs.parameter('separator', yaqltypes.String(nullable=True))
@specs.parameter('max_splits', int)
@specs.method
def split(string, separator=None, max_splits=-1):
    return string.split(separator, max_splits)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('separator', yaqltypes.String(nullable=True))
@specs.parameter('max_splits', int)
@specs.method
def right_split(string, separator=None, max_splits=-1):
    return string.rsplit(separator, max_splits)


@specs.parameter('sequence', yaqltypes.Iterable())
@specs.parameter('separator', yaqltypes.String())
@specs.inject('str_delegate', yaqltypes.Delegate('str'))
@specs.method
def join(sequence, separator, str_delegate):
    return separator.join(six.moves.map(str_delegate, sequence))


@specs.parameter('sequence', yaqltypes.Iterable())
@specs.parameter('separator', yaqltypes.String())
@specs.inject('str_delegate', yaqltypes.Delegate('str'))
@specs.method
def join_(separator, sequence, str_delegate):
    return join(sequence, separator, str_delegate)


@specs.parameter('value', nullable=True)
def str_(value):
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
    return string.strip(chars)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('chars', yaqltypes.String(nullable=True))
@specs.method
def trim_left(string, chars=None):
    return string.lstrip(chars)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('chars', yaqltypes.String(nullable=True))
@specs.method
def trim_right(string, chars=None):
    return string.rstrip(chars)


@specs.parameter('string', yaqltypes.String(nullable=True))
@specs.parameter('chars', yaqltypes.String(nullable=True))
@specs.extension_method
def norm(string, chars=None):
    if string is None:
        return None
    value = string.strip(chars)
    return None if not value else value


@specs.parameter('string', yaqltypes.String(nullable=True))
@specs.parameter('trim_spaces', bool, alias='trim')
@specs.parameter('chars', yaqltypes.String(nullable=True))
@specs.extension_method
def is_empty(string, trim_spaces=True, chars=None):
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
    return string.replace(old, new, count)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('replacements', utils.MappingType)
@specs.parameter('count', int)
@specs.inject('str_func', yaqltypes.Delegate('str'))
@specs.method
@specs.name('replace')
def replace_with_dict(string, str_func, replacements, count=-1):
    for key, value in six.iteritems(replacements):
        string = string.replace(str_func(key), str_func(value), count)
    return string


@specs.parameter('__format_string', yaqltypes.String())
@specs.extension_method
def format_(__format_string, *args, **kwargs):
    return __format_string.format(*args, **kwargs)


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', int)
@specs.name('#operator_*')
def string_by_int(left, right, engine):
    utils.limit_memory_usage(engine, (-right + 1, u''), (right, left))
    return left * right


@specs.parameter('left', yaqltypes.String())
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_in')
def in_(left, right):
    return left in right


@specs.parameter('left', int)
@specs.parameter('right', yaqltypes.String())
@specs.name('#operator_*')
def int_by_string(left, right, engine):
    return string_by_int(right, left, engine)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('start', int)
@specs.parameter('length', int)
@specs.method
def substring(string, start, length=-1):
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
    return string.find(sub, start)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('sub', yaqltypes.String())
@specs.parameter('start', int)
@specs.parameter('length', int)
@specs.method
def index_of_(string, sub, start, length):
    if length < 0:
        length = len(string)
    if start < 0:
        start += len(string)
    return string.find(sub, start, length)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('sub', yaqltypes.String())
@specs.parameter('start', int)
@specs.method
def last_index_of(string, sub, start=0):
    return string.rfind(sub, start)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('sub', yaqltypes.String())
@specs.parameter('start', int)
@specs.parameter('length', int)
@specs.method
def last_index_of_(string, sub, start, length):
    if length < 0:
        length = len(string)
    if start < 0:
        start += len(string)
    return string.rfind(sub, start, length)


@specs.parameter('string', yaqltypes.String())
@specs.method
def to_char_array(string):
    return tuple(string)


def characters(
        digits=False, hexdigits=False,
        ascii_lowercase=False, ascii_uppercase=False,
        ascii_letters=False, letters=False,
        octdigits=False, punctuation=False, printable=False,
        lowercase=False, uppercase=False, whitespace=False):
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
    return isinstance(arg, six.string_types)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('prefixes', yaqltypes.String())
@specs.method
def starts_with(string, *prefixes):
    return string.startswith(prefixes)


@specs.parameter('string', yaqltypes.String())
@specs.parameter('suffixes', yaqltypes.String())
@specs.method
def ends_with(string, *suffixes):
    return string.endswith(suffixes)


@specs.parameter('num', yaqltypes.Number(nullable=True))
def hex_(num):
    return hex(num)


def register(context):
    context.register_function(gt)
    context.register_function(lt)
    context.register_function(gte)
    context.register_function(lte)
    context.register_function(eq)
    context.register_function(neq)
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
