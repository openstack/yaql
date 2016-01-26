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

import codecs
import re

import six

from yaql.language import exceptions


NEVER_MATCHING_RE = '(?!x)x'
ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)


def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')
    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


# noinspection PyPep8Naming
class Lexer(object):
    t_ignore = ' \t\r\n'

    literals = '()],}'
    keywords = {
        'true': 'TRUE',
        'false': 'FALSE',
        'null': 'NULL'
    }

    keyword_to_val = {
        'TRUE': True,
        'FALSE': False,
        'NULL': None
    }

    def __init__(self, yaql_operators):
        self._operators_table = yaql_operators.operators
        self.tokens = [
            'KEYWORD_STRING',
            'QUOTED_STRING',
            'NUMBER',
            'FUNC',
            'DOLLAR',
            'INDEXER',
            'MAPPING',
            'MAP'
        ] + list(self.keywords.values())
        for op_symbol, op_record in six.iteritems(self._operators_table):
            if op_symbol in ('[]', '{}'):
                continue
            lexem_name = op_record[2]
            setattr(self, 't_' + lexem_name, re.escape(op_symbol))
            self.tokens.append(lexem_name)
        self.t_MAPPING = re.escape(yaql_operators.name_value_op) \
            if yaql_operators.name_value_op else NEVER_MATCHING_RE
        self.t_INDEXER = '\\[' \
            if '[]' in self._operators_table else NEVER_MATCHING_RE
        self.t_MAP = '{' \
            if '{}' in self._operators_table else NEVER_MATCHING_RE

    @staticmethod
    def t_DOLLAR(t):
        """
        \\$\\w*
        """
        return t

    @staticmethod
    def t_NUMBER(t):
        """
        \\b\\d+(\\.?\\d+)?\\b
        """
        if '.' in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    @staticmethod
    def t_FUNC(t):
        """
        \\b[^\\W\\d]\\w*\\(
        """
        val = t.value[:-1]
        t.value = val
        return t

    def t_KEYWORD_STRING(self, t):
        """
        (?!__)\\b[^\\W\\d]\\w*\\b
        """
        if t.value in self._operators_table:
            t.type = self._operators_table[t.value][2]
        else:
            t.type = self.keywords.get(t.value, 'KEYWORD_STRING')
            t.value = self.keyword_to_val.get(t.type, t.value)
        return t

    @staticmethod
    def t_QUOTED_STRING(t):
        """
        '([^'\\\\]|\\\\.)*'
        """
        t.value = decode_escapes(t.value[1:-1])
        return t

    @staticmethod
    def t_DOUBLE_QUOTED_STRING(t):
        """
        "([^"\\\\]|\\\\.)*"
        """
        t.value = decode_escapes(t.value[1:-1])
        t.type = 'QUOTED_STRING'
        return t

    @staticmethod
    def t_QUOTED_VERBATIM_STRING(t):
        """
        `([^`\\\\]|\\\\.)*`
        """
        t.value = t.value[1:-1].replace('\\`', '`')
        t.type = 'QUOTED_STRING'
        return t

    @staticmethod
    def t_error(t):
        raise exceptions.YaqlLexicalException(t.value[0], t.lexpos)
