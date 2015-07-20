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


import re

import six

from yaql.language import specs
from yaql.language import yaqltypes

REGEX_TYPE = type(re.compile('.'))


@specs.parameter('pattern', yaqltypes.String())
def regex(pattern, ignore_case=False, multi_line=False, dot_all=False):
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
    return regexp.search(string) is not None


@specs.parameter('string', yaqltypes.String())
@specs.parameter('regexp', yaqltypes.String())
@specs.method
def matches_(string, regexp):
    return re.search(regexp, string) is not None


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.name('#operator_=~')
def matches_operator_regex(string, regexp):
    return regexp.search(string) is not None


@specs.parameter('pattern', yaqltypes.String())
@specs.parameter('string', yaqltypes.String())
@specs.name('#operator_=~')
def matches_operator_string(string, pattern):
    return re.search(pattern, string) is not None


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.name('#operator_!~')
def not_matches_operator_regex(string, regexp):
    return regexp.search(string) is None


@specs.parameter('pattern', yaqltypes.String())
@specs.parameter('string', yaqltypes.String())
@specs.name('#operator_!~')
def not_matches_operator_string(string, pattern):
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

    for key, value, in six.itervalues(match.groupdict()):
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
    res = regexp.search(string)
    if res is None:
        return None
    if selector is None:
        return res.group()
    _publish_match(context, res)
    return selector(context)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('selector', yaqltypes.Lambda(with_context=True))
@specs.method
def search_all(context, regexp, string, selector=None):
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
    return regexp.split(string, max_split)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('max_split', int)
@specs.method
@specs.name('split')
def split_string(string, regexp, max_split=0):
    return regexp.split(string, max_split)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('repl', yaqltypes.String())
@specs.parameter('count', int)
@specs.method
def replace(regexp, string, repl, count=0):
    return regexp.sub(repl, string, count)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('repl', yaqltypes.String())
@specs.parameter('count', int)
@specs.method
@specs.name('replace')
def replace_string(string, regexp, repl, count=0):
    return replace(regexp, string, repl, count)


@specs.parameter('regexp', REGEX_TYPE)
@specs.parameter('string', yaqltypes.String())
@specs.parameter('repl', yaqltypes.Lambda(with_context=True))
@specs.parameter('count', int)
@specs.method
def replace_by(context, regexp, string, repl, count=0):
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
    return replace_by(context, regexp, string, repl, count)


@specs.parameter('string', yaqltypes.String())
def escape_regex(string):
    return re.escape(string)


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
