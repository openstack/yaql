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

import sys

import yaql
from yaql.language import exceptions
from yaql.language import utils


class Expression:
    def __call__(self, receiver, context, engine):
        pass


class Function(Expression):
    def __init__(self, name, *args):
        self.name = name
        self.args = args
        self.uses_receiver = True

    def __call__(self, receiver, context, engine):
        return context(self.name, engine, receiver, context)(*self.args)

    def __str__(self):
        return '{}({})'.format(self.name, ', '.join(map(str, self.args)))


class BinaryOperator(Function):
    def __init__(self, op, obj1, obj2, alias):
        if alias is None:
            func_name = '#operator_' + op
        else:
            func_name = '*' + alias
        self.operator = op
        super().__init__(func_name, obj1, obj2)
        self.uses_receiver = False


class UnaryOperator(Function):
    def __init__(self, op, obj, alias):
        if alias is None:
            func_name = '#unary_operator_' + op
        else:
            func_name = '*' + alias
        self.operator = op
        super().__init__(func_name, obj)
        self.uses_receiver = False


class IndexExpression(Function):
    def __init__(self, value, *args):
        super().__init__('#indexer', value, *args)
        self.uses_receiver = False


class ListExpression(Function):
    def __init__(self, *args):
        super().__init__('#list', *args)
        self.uses_receiver = False


class MapExpression(Function):
    def __init__(self, *args):
        super().__init__('#map', *args)
        self.uses_receiver = False


class GetContextValue(Function):
    def __init__(self, path):
        super().__init__('#get_context_data', path)
        self.path = path
        self.uses_receiver = False

    def __str__(self):
        return self.path.value


class Constant(Expression):
    def __init__(self, value):
        self.value = value
        self.uses_receiver = False

    def __str__(self):
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return str(self.value)

    def __call__(self, receiver, context, engine):
        return self.value


class KeywordConstant(Constant):
    pass


class Wrap(Expression):
    def __init__(self, expression):
        self.expr = expression
        self.uses_receiver = False

    def __str__(self):
        return str(self.expr)

    def __call__(self, receiver, context, engine):
        return self.expr(receiver, context, engine)


class MappingRuleExpression(Expression):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.uses_receiver = False

    def __str__(self):
        return '{} => {}'.format(self.source, self.destination)

    def __call__(self, receiver, context, engine):
        return utils.MappingRule(
            self.source(receiver, context, engine),
            self.destination(receiver, context, engine))


class Statement(Function):
    def __init__(self, expression, engine):
        self.expression = expression
        self.uses_receiver = False
        self.engine = engine
        super().__init__('#finalize', expression)

    def __call__(self, receiver, context, engine):
        if not context.collect_functions('#finalize'):
            context = context.create_child_context()
            context.register_function(lambda x: x, name='#finalize')
        try:
            return super().__call__(receiver, context, engine)
        except exceptions.WrappedException as e:
            raise e.wrapped.with_traceback(sys.exc_info()[2])

    def evaluate(self, data=utils.NO_VALUE, context=None):
        if context is None or context is utils.NO_VALUE:
            context = yaql.create_context()
        if data is not utils.NO_VALUE:
            if self.engine.options.get('yaql.convertInputData', True):
                context['$'] = utils.convert_input_data(data)
            else:
                context['$'] = data
        return self(utils.NO_VALUE, context, self.engine)

    def __str__(self):
        return str(self.expression)
