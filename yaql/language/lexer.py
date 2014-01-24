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
from yaql.language.exceptions import YaqlLexicalException

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

right_associative = [':']


unary_prefix = {
    '-': "UNARY_MINUS",
    '+': "UNARY_PLUS",
    '~': "UNARY_TILDE",
    '!': "UNARY_EXPL"
}

op_to_level = {
    'abc': 0,
    '|' : 1,
    '^' : 2,
    '&' : 3,
    '<' : 4,
    '>' : 4,
    '=' : 5,
    '!' : 5,
    '+' : 6,
    '-' : 6,
    '*' : 7,
    '/' : 7,
    '%' : 7,
    '.' : 8
}

ops = {
    (0, 'l'): "LVL0_LEFT",
    (0, 'r'): "LVL0_RIGHT",
    (1, 'l'): "LVL1_LEFT",
    (1, 'r'): "LVL1_RIGHT",
    (2, 'l'): "LVL2_LEFT",
    (2, 'r'): "LVL2_RIGHT",
    (3, 'l'): "LVL3_LEFT",
    (3, 'r'): "LVL3_RIGHT",
    (4, 'l'): "LVL4_LEFT",
    (4, 'r'): "LVL4_RIGHT",
    (5, 'l'): "LVL5_LEFT",
    (5, 'r'): "LVL5_RIGHT",
    (6, 'l'): "LVL6_LEFT",
    (6, 'r'): "LVL6_RIGHT",
    (7, 'l'): "LVL7_LEFT",
    (7, 'r'): "LVL7_RIGHT",
    (8, 'l'): "LVL8_LEFT",
    (8, 'r'): "LVL8_RIGHT",
    (9, 'l'): "LVL9_LEFT",
    (9, 'r'): "LVL9_RIGHT"
}


tokens = [
    'STRING',
    'QUOTED_STRING',
    'NUMBER',
    'FUNC',
    'FILTER',
    'NOT',
    'DOLLAR'
] + list(keywords.values())+list(ops.values()) + list(unary_prefix.values())

literals = "()],"

t_ignore = ' \t\r\n'


def t_DOLLAR(t):
    """
    \\$\\w*
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
    \\b\\w+\\(|'(?:[^'\\\\]|\\\\.)*'\\(
    """
    val = t.value[:-1].replace('\\', '').strip('\'')
    t.value = val
    return t


def t_FILTER(t):
    """
   (?<!\\s)\\[
    """
    return t


def t_NOT(t):
    """
    \\bnot\\b
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


def t_CHAR_ORB(t):
    """
    [!@#%^&*=.:;`~\\-><+/]+
    """
    if t.value in unary_prefix:
        t.type = unary_prefix[t.value]
    else:
        t.type = get_orb_op_type(t.value[0], t.value[-1])
    return t



def get_orb_op_type(first_char, last_char):
    if first_char.isalpha() or first_char == '_':
        level = op_to_level['abc']
    else:
        level = op_to_level.get(first_char, max(op_to_level.values())+1)
    asc = 'r' if last_char in right_associative else 'l'
    return ops.get((level, asc))


def t_error(t):
    raise YaqlLexicalException(t.value[0], t.lexpos)

lexer = lex.lex()
