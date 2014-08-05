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

import types
import tempfile
import uuid

import ply.yacc as yacc

import expressions
import exceptions
import lexer


tokens = lexer.tokens


def p_value_to_const(p):
    """
    value : STRING
          | QUOTED_STRING
          | NUMBER
          | TRUE
          | FALSE
          | NULL
    """
    p[0] = expressions.Constant(p[1])


def p_value_to_dollar(p):
    """
    value : DOLLAR
    """
    p[0] = expressions.GetContextValue(expressions.Constant(p[1]))


def p_value_to_symbol(p):
    """
    symbol : SYMBOL
    """
    symbol_parts = p[1].split(':')
    sns = symbol_parts[0]
    name = symbol_parts[1]
    expanding = expressions.UnaryOperator(':', expressions.Constant(sns))

    p[0] = expressions.Function('#validate', None, expanding,
                                expressions.Constant(name))


def p_attribution(p):
    """
    value : value '.' STRING
          | value '.' QUOTED_STRING
    """
    p[0] = expressions.Att(p[1], expressions.Constant(p[3]))


def p_attribution_to_symbol(p):
    """
    value : value '.' symbol
    """
    p[0] = expressions.Att(p[1], p[3])


def p_val_to_function(p):
    """
    value : func
          | symbol
    """
    p[0] = p[1]


def p_method_no_args(p):
    """
    func : value '.' FUNC ')'
    """
    p[0] = expressions.Function(p[3], p[1])


def p_arg_definition(p):
    """
    arg : value
    """
    p[0] = p[1]


def p_method_w_args(p):
    """
    func : value '.' FUNC arg ')'
    """
    if isinstance(p[4], types.ListType):
        arg = p[4]
    else:
        arg = [p[4]]
    p[0] = expressions.Function(p[3], p[1], *arg)


def p_function_no_args(p):
    """
    func : FUNC ')'
    """
    p[0] = expressions.Function(p[1], None)


def p_function_w_args(p):
    """
    func : FUNC arg ')'
    """
    if isinstance(p[2], types.ListType):
        arg = p[2]
    else:
        arg = [p[2]]
    p[0] = expressions.Function(p[1], None, *arg)


def p_arg_list(p):
    """
    arg : arg ',' arg
    """
    val_list = []
    if isinstance(p[1], types.ListType):
        val_list += p[1]
    else:
        val_list.append(p[1])
    if isinstance(p[3], types.ListType):
        val_list += p[3]
    else:
        val_list.append(p[3])

    p[0] = val_list


def p_val_with_binary_op(p):
    """
    value : value '+' value
          | value '-' value
          | value '*' value
          | value '/' value
          | value '>' value
          | value '<' value
          | value '=' value
          | value NE value
          | value LE value
          | value GE value
          | value OR value
          | value AND value
          | value IS value
          | value IN value
    """
    p[0] = expressions.BinaryOperator(p[2], p[1], p[3])


def p_val_with_unary_op(p):
    """
    value : NOT value
    """
    p[0] = expressions.UnaryOperator(p[1], p[2])


def p_val_in_parenthesis(p):
    """
    value : '(' value ')'
    """
    p[0] = expressions.Wrap(p[2])


def p_val_w_filter(p):
    """
    value : value FILTER value ']'
    """
    p[0] = expressions.Filter(p[1], p[3])


def p_val_tuple(p):
    """
    value : value TUPLE value
    """
    p[0] = expressions.Tuple.create_tuple(p[1], p[3])


def p_error(p):
    if p:
        raise exceptions.YaqlGrammarException(p.value, p.lexpos)
    else:
        raise exceptions.YaqlGrammarException(None, None)


precedence = (
    ('left', 'TUPLE'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'NOT'),
    ('nonassoc', '>', '<', '=', 'NE', 'LE', 'GE', 'IS', 'IN'),
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('left', ','),
    ('left', 'FILTER', ']'),
    ('left', '.'),
    ('left', 'SYMBOL')
)

parser = None


def parse(expression, write_tables=False, tabmodule=None):
    global parser
    if parser is None:
        parser = yacc.yacc(
            debug=False,
            outputdir=tempfile.gettempdir(),
            write_tables=(1 if not write_tables else 0),
            tabmodule=tabmodule or 'yaql_%s' % uuid.uuid4().hex
        )
    return parser.parse(expression)
