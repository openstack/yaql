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

import collections
import re
import uuid

from ply import lex
from ply import yacc

from yaql.language import exceptions
from yaql.language import expressions
from yaql.language import lexer
from yaql.language import parser
from yaql.language import utils


OperatorType = collections.namedtuple('OperatorType', [
    'PREFIX_UNARY', 'SUFFIX_UNARY',
    'BINARY_LEFT_ASSOCIATIVE', 'BINARY_RIGHT_ASSOCIATIVE',
    'NAME_VALUE_PAIR'
])(
    PREFIX_UNARY='PREFIX_UNARY',
    SUFFIX_UNARY='SUFFIX_UNARY',
    BINARY_LEFT_ASSOCIATIVE='BINARY_LEFT_ASSOCIATIVE',
    BINARY_RIGHT_ASSOCIATIVE='BINARY_RIGHT_ASSOCIATIVE',
    NAME_VALUE_PAIR='NAME_VALUE_PAIR'
)


class YaqlOperators(object):
    def __init__(self, operators, name_value_op=None):
        self.operators = operators
        self.name_value_op = name_value_op


class YaqlEngine(object):
    def __init__(self, ply_lexer, ply_parser, options, factory):
        self._lexer = ply_lexer
        self._parser = ply_parser
        self._options = utils.FrozenDict(options or {})
        self._factory = factory

    @property
    def lexer(self):
        return self._lexer

    @property
    def parser(self):
        return self._parser

    @property
    def options(self):
        return self._options

    @property
    def factory(self):
        return self._factory

    def __call__(self, expression, options=None):
        if options:
            return self.copy(options)(expression)

        return expressions.Statement(
            self.parser.parse(expression, lexer=self.lexer), self)

    def copy(self, options):
        opt = dict(self._options)
        opt.update(options)
        return YaqlEngine(self._lexer, self._parser, opt, self._factory)


class YaqlFactory(object):
    def __init__(self, keyword_operator='=>', allow_delegates=False):
        self._keyword_operator = keyword_operator
        self._allow_delegates = allow_delegates
        self.operators = self._standard_operators()
        if keyword_operator:
            self.operators.insert(0, (keyword_operator,
                                      OperatorType.NAME_VALUE_PAIR))

    @property
    def keyword_operator(self):
        return self._keyword_operator

    @property
    def allow_delegates(self):
        return self._allow_delegates

    # noinspection PyMethodMayBeStatic
    def _standard_operators(self):
        return [
            ('.', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            ('?.', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            (),
            ('[]', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            ('{}', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            (),
            ('+', OperatorType.PREFIX_UNARY),
            ('-', OperatorType.PREFIX_UNARY),
            (),
            ('=~', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            ('!~', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            (),
            ('*', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            ('/', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            ('mod', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            (),
            ('+', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            ('-', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            (),
            ('>', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            ('<', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            ('>=', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            ('<=', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            ('!=', OperatorType.BINARY_LEFT_ASSOCIATIVE, 'not_equal'),
            ('=', OperatorType.BINARY_LEFT_ASSOCIATIVE, 'equal'),
            ('in', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            (),
            ('not', OperatorType.PREFIX_UNARY),
            (),
            ('and', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            (),
            ('or', OperatorType.BINARY_LEFT_ASSOCIATIVE),
            (),
            ('->', OperatorType.BINARY_RIGHT_ASSOCIATIVE),
        ]

    def insert_operator(self, existing_operator, existing_operator_binary,
                        new_operator, new_operator_type, create_group,
                        new_operator_alias=None):
        binary_types = (OperatorType.BINARY_RIGHT_ASSOCIATIVE,
                        OperatorType.BINARY_LEFT_ASSOCIATIVE)
        unary_types = (OperatorType.PREFIX_UNARY, OperatorType.SUFFIX_UNARY)
        position = 0
        if existing_operator is not None:
            position = -1
            for i, t in enumerate(self.operators):
                if len(t) < 2 or t[0] != existing_operator:
                    continue
                if existing_operator_binary and t[1] not in binary_types:
                    continue
                if not existing_operator_binary and t[1] not in unary_types:
                    continue
                position = i
                break
            if position < 0:
                raise ValueError('Operator {0} is not found'.format(
                    existing_operator))
            while position < len(self.operators) and len(
                    self.operators[position]) > 1:
                position += 1
        if create_group:
            if position == len(self.operators):
                self.operators.append(())
                position += 1
            else:
                while position < len(self.operators) and len(
                        self.operators[position]) < 2:
                    position += 1
                self.operators.insert(position, ())
        self.operators.insert(
            position, (new_operator, new_operator_type, new_operator_alias))

    @staticmethod
    def _name_generator():
        value = 1
        while True:
            t = value
            chars = []
            while t:
                chars.append(chr(ord('A') + t % 26))
                t //= 26
            yield ''.join(chars)
            value += 1

    def _build_operator_table(self, name_generator):
        operators = {}
        name_value_op = None
        precedence = 1
        for record in self.operators:
            if not record:
                precedence += 1
                continue
            up, bp, name, alias = operators.get(record[0], (0, 0, '', None))
            if record[1] == OperatorType.NAME_VALUE_PAIR:
                if name_value_op is not None:
                    raise exceptions.InvalidOperatorTableException(record[0])
                name_value_op = record[0]
                continue
            if record[1] == OperatorType.PREFIX_UNARY:
                if up:
                    raise exceptions.InvalidOperatorTableException(record[0])
                up = precedence
            elif record[1] == OperatorType.SUFFIX_UNARY:
                if up:
                    raise exceptions.InvalidOperatorTableException(record[0])
                up = -precedence
            elif record[1] == OperatorType.BINARY_LEFT_ASSOCIATIVE:
                if bp:
                    raise exceptions.InvalidOperatorTableException(record[0])
                bp = precedence
            elif record[1] == OperatorType.BINARY_RIGHT_ASSOCIATIVE:
                if bp:
                    raise exceptions.InvalidOperatorTableException(record[0])
                bp = -precedence
            if record[0] == '[]':
                name = 'INDEXER'
            elif record[0] == '{}':
                name = 'MAP'
            else:
                name = name or 'OP_' + next(name_generator)
            operators[record[0]] = (
                up, bp, name, record[2] if len(record) > 2 else None)
        return YaqlOperators(operators, name_value_op)

    # noinspection PyMethodMayBeStatic
    def _create_lexer(self, operators):
        return lexer.Lexer(operators)

    # noinspection PyMethodMayBeStatic
    def _create_parser(self, lexer_rules, operators):
        return parser.Parser(lexer_rules, operators, self)

    def create(self, options=None):
        names = self._name_generator()
        operators = self._build_operator_table(names)
        lexer_rules = self._create_lexer(operators)
        ply_lexer = lex.lex(object=lexer_rules,
                            reflags=re.UNICODE | re.VERBOSE)
        ply_parser = yacc.yacc(
            module=self._create_parser(lexer_rules, operators),
            debug=False if not options else options.get('yaql.debug', False),
            tabmodule='m' + uuid.uuid4().hex, write_tables=False)

        return YaqlEngine(ply_lexer, ply_parser, options, self)
