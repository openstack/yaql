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

import six

from yaql.language import exceptions
from yaql.language import expressions
from yaql.language import utils


class Parser(object):
    def __init__(self, lexer, yaql_operators, engine):
        self.tokens = lexer.tokens
        self._aliases = {}
        self._generate_operator_funcs(yaql_operators, engine)

    def _generate_operator_funcs(self, yaql_operators, engine):
        binary_doc = ''
        unary_doc = ''
        precedence_dict = {}

        for up, bp, op_name, op_alias in yaql_operators.operators.values():
            self._aliases[op_name] = op_alias
            if up:
                l = precedence_dict.setdefault(
                    (abs(up), 'l' if up > 0 else 'r'), [])
                l.append('UNARY_' + op_name if bp else op_name)
                unary_doc += ('value : ' if not unary_doc else '\n| ')
                spec_prefix = '{0} value' if up > 0 else 'value {0}'
                if bp:
                    unary_doc += (spec_prefix + ' %prec UNARY_{0}').format(
                        op_name)
                else:
                    unary_doc += spec_prefix.format(op_name)
            if bp:
                l = precedence_dict.setdefault(
                    (abs(bp), 'l' if bp > 0 else 'r'), [])
                if op_name == 'INDEXER':
                    l.extend(('LIST', 'INDEXER'))
                elif op_name == 'MAP':
                    l.append('MAP')
                else:
                    l.append(op_name)
                    binary_doc += ((
                        'value : ' if not binary_doc else '\n| ') +
                        'value {0} value'.format(op_name))

        # noinspection PyProtectedMember
        def p_binary(this, p):
            alias = this._aliases.get(p.slice[2].type)
            p[0] = expressions.BinaryOperator(p[2], p[1], p[3], alias)

        # noinspection PyProtectedMember
        def p_unary(this, p):
            if p[1] in yaql_operators.operators:
                alias = this._aliases.get(p.slice[1].type)
                p[0] = expressions.UnaryOperator(p[1], p[2], alias)
            else:
                alias = this._aliases.get(p.slice[2].type)
                p[0] = expressions.UnaryOperator(p[2], p[1], alias)

        p_binary.__doc__ = binary_doc
        self.p_binary = six.create_bound_method(p_binary, self)
        p_unary.__doc__ = unary_doc
        self.p_unary = six.create_bound_method(p_unary, self)

        precedence = []
        for i in range(1, len(precedence_dict) + 1):
            for oa in ('r', 'l'):
                value = precedence_dict.get((i, oa))
                if value:
                    precedence.append(
                        (('left',) if oa is 'l' else ('right',)) +
                        tuple(value)
                    )
        precedence.insert(0, ('left', ','))
        precedence.reverse()
        self.precedence = tuple(precedence)

        def p_value_call(this, p):
            """
            func : value '(' args ')'
            """
            arg = ()
            if len(p) > 4:
                arg = p[3]
            p[0] = expressions.Function('#call', p[1], *arg)

        if engine.allow_delegates:
            self.p_value_call = six.create_bound_method(p_value_call, self)

    @staticmethod
    def p_value_to_const(p):
        """
        value : QUOTED_STRING
              | NUMBER
              | TRUE
              | FALSE
              | NULL
        """
        p[0] = expressions.Constant(p[1])

    @staticmethod
    def p_keyword_constant(p):
        """
        value : KEYWORD_STRING
        """
        p[0] = expressions.KeywordConstant(p[1])

    @staticmethod
    def p_value_to_dollar(p):
        """
        value : DOLLAR
        """
        p[0] = expressions.GetContextValue(expressions.Constant(p[1]))

    @staticmethod
    def p_val_in_parenthesis(p):
        """
        value : '(' value ')'
        """
        p[0] = expressions.Wrap(p[2])

    @staticmethod
    def p_args(p):
        """
        args : arglist
             | named_arglist
             | arglist ',' named_arglist
             | incomplete_arglist ',' named_arglist
             |
        """
        if len(p) == 1:
            p[0] = []
        elif len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[3]

    @staticmethod
    def p_indexer(p):
        """
        value : value INDEXER args ']'
        """
        p[0] = expressions.IndexExpression(p[1], *p[3])

    @staticmethod
    def p_list(p):
        """
        value : INDEXER args ']' %prec LIST
        """
        p[0] = expressions.ListExpression(*p[2])

    @staticmethod
    def p_map(p):
        """
        value : MAP args '}'
        """
        p[0] = expressions.MapExpression(*p[2])

    @staticmethod
    def p_val_to_function(p):
        """
        value : func
        """
        p[0] = p[1]

    @staticmethod
    def p_named_arg_definition(p):
        """
        named_arg : value MAPPING value
        """
        p[0] = expressions.MappingRuleExpression(p[1], p[3])

    @staticmethod
    def p_arg_list(p):
        """
        arglist : value
                | ',' arglist
                | arglist ',' arglist
                | incomplete_arglist ',' arglist
        """
        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 3:
            p[0] = [utils.NO_VALUE] + p[2]
        elif len(p) == 4:
            p[0] = p[1] + p[3]

    @staticmethod
    def p_incomplete_arg_list(p):
        """
        incomplete_arglist : arglist ','
        """
        p[0] = p[1] + [utils.NO_VALUE]

    @staticmethod
    def p_named_arg_list(p):
        """
        named_arglist : named_arg
                      | named_arglist ',' named_arg
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    @staticmethod
    def p_function(p):
        """
        func : FUNC args ')'
        """
        arg = ()
        if len(p) > 3:
            arg = p[2]
        p[0] = expressions.Function(p[1], *arg)

    @staticmethod
    def p_error(p):
        if p:
            raise exceptions.YaqlGrammarException(
                p.lexer.lexdata, p.value, p.lexpos)
        else:
            raise exceptions.YaqlGrammarException(None, None, None)
