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

import ply.yacc as yacc

from yaql.language import lexer, expressions, exceptions


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


def p_val_to_function(p):
    """
    value : func
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
    p[0] = expressions.Function(p[1])


def p_function_w_args(p):
    """
    func : FUNC arg ')'
    """
    if isinstance(p[2], types.ListType):
        arg = p[2]
    else:
        arg = [p[2]]
    p[0] = expressions.Function(p[1], *arg)


def p_binary(p):
    """
    value : value STRING value
          | value LVL0_LEFT value
          | value LVL0_RIGHT value
          | value LVL1_LEFT value
          | value LVL1_RIGHT value
          | value LVL2_LEFT value
          | value LVL2_RIGHT value
          | value LVL3_LEFT value
          | value LVL3_RIGHT value
          | value LVL4_LEFT value
          | value LVL4_RIGHT value
          | value LVL5_LEFT value
          | value LVL5_RIGHT value
          | value LVL6_LEFT value
          | value LVL6_RIGHT value
          | value LVL7_LEFT value
          | value LVL7_RIGHT value
          | value LVL8_LEFT value
          | value LVL8_RIGHT value
          | value LVL9_LEFT value
          | value LVL9_RIGHT value
          | value UNARY_PLUS value
          | value UNARY_MINUS value
          | value UNARY_EXPL value
          | value UNARY_TILDE value
    """
    p[0] = expressions.BinaryOperator(p[2], p[1], p[3])



def p_unary_prefix(p):
    """
    value : UNARY_TILDE value
          | UNARY_PLUS value
          | UNARY_EXPL value
          | UNARY_MINUS value
          | NOT value
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


# def p_val_tuple(p):
#     """
#     value : value TUPLE value
#     """
#     p[0] = expressions.Tuple.create_tuple(p[1], p[3])


def p_error(p):
    if p:
        raise exceptions.YaqlGrammarException(p.value, p.lexpos)
    else:
        raise exceptions.YaqlGrammarException(None, None)


precedence = (
    ('left', lexer.ops[(0, 'l')], 'STRING', ','),
    ('right', lexer.ops[(0, 'r')]),
    ('left', lexer.ops[(1, 'l')]),
    ('right', lexer.ops[(1, 'r')]),
    ('left', lexer.ops[(2, 'l')]),
    ('right', lexer.ops[(2, 'r')]),
    ('left', lexer.ops[(3, 'l')]),
    ('right', lexer.ops[(3, 'r')]),
    ('left', lexer.ops[(4, 'l')]),
    ('right', lexer.ops[(4, 'r')]),
    ('left', lexer.ops[(5, 'l', )], 'NOT', 'UNARY_EXPL'),
    ('right', lexer.ops[(5, 'r')]),
    ('left', lexer.ops[(6, 'l')], 'UNARY_PLUS', 'UNARY_MINUS'),
    ('right', lexer.ops[(6, 'r')]),
    ('left', lexer.ops[(7, 'l')]),
    ('right', lexer.ops[(7, 'r')]),
    ('left', lexer.ops[(8, 'l')]),
    ('right', lexer.ops[(8, 'r')]),
    ('left', lexer.ops[(9, 'l')], 'UNARY_TILDE'),
    ('right', lexer.ops[(9, 'r')]),

)

parser = yacc.yacc(debug=False, outputdir=tempfile.gettempdir(), tabmodule='parser_table')
# parser = yacc.yacc()


def parse(expression):
    return parser.parse(expression)
