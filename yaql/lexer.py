#    Copyright (c) 2013 Mirantis, Inc.
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

import ply.lex as lex
from yaql.exceptions import YaqlLexicalException

keywords = {
    'true': 'TRUE',
    'false': 'FALSE',
    'null': 'NULL'
}

keywords_to_val = {
    'TRUE': True,
    'FALSE': False,
    'NULL': None
}

tokens = [
    'SYMBOL',
    'STRING',
    'QUOTED_STRING',
    'NUMBER',
    'FUNC',
    'GE',
    'LE',
    'NE',
    'FILTER',
    'TUPLE',
    'OR',
    'AND',
    'NOT',
    'IS',
    'IN',
    'DOLLAR'
] + list(keywords.values())

literals = "+-*/.()]><=,"

t_ignore = ' \t'


t_GE = '>='
t_LE = '<='
t_NE = '!='

t_TUPLE = '=>'


def t_SYMBOL(t):
    """
    \\b\\w+\\:\\w+\\b
    """
    return t


def t_DOLLAR(t):
    """
    \\$\\w*
    """
    return t


def t_AND(t):
    """
    \\band\\b
    """
    return t


def t_OR(t):
    """
    \\bor\\b
    """
    return t


def t_NOT(t):
    """
    \\bnot\\b
    """
    return t


def t_IS(t):
    """
    \\bis\\b
    """
    return t


def t_IN(t):
    """
    \\bin\\b
    """
    return t


def t_NUMBER(t):
    """
    \\b\\d+(\\.?\\d+)?\\b
    """
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t


def t_FUNC(t):
    """
    \\b\\w+\\(
    """
    t.value = t.value[:-1]
    return t

#  (?<=\\w)\\[|(?<=\\])\\[|(?<=\\$)\\[


def t_FILTER(t):
    """
   (?<!\\s)\\[
    """
    return t


def t_STRING(t):
    """
    \\b\\w+\\b
    """
    t.type = keywords.get(t.value, 'STRING')
    t.value = keywords_to_val.get(t.type, t.value)
    return t


def t_QUOTED_STRING(t):
    """
    '(?:[^'\\\\]|\\\\.)*'
    """
    t.value = t.value[1:-1].replace('\\', '')

    return t


def t_error(t):
    raise YaqlLexicalException(t.value[0], t.lexpos)


lexer = lex.lex()
