# Copyright (c) 2015 Mirantis, Inc.
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

import io
import sys

import yaql
from yaql.language import exceptions
from yaql.language import factory
from yaql.language import specs
from yaql.language import yaqltypes
from yaql import tests


class TestEngine(tests.TestCase):
    def test_parser_grammar(self):
        # replace stderr with cString to write to
        copy = sys.stderr
        sys.stderr = io.StringIO()
        try:
            debug_opts = dict(self.engine_options)
            debug_opts['yaql.debug'] = True
            yaql.factory.YaqlFactory().create(options=debug_opts)
            sys.stderr.seek(0)
            err_out = sys.stderr.read()
            self.assertEqual('Generating LALR tables\n', err_out)
        finally:
            # put stderr back
            sys.stderr = copy

    def test_no_function_registered(self):
        self.assertRaises(
            exceptions.NoFunctionRegisteredException,
            self.eval, 'kjhfksjdhfk()')

    def test_no_method_registered(self):
        self.assertRaises(
            exceptions.NoMethodRegisteredException,
            self.eval, '[1,2].kjhfksjdhfk($)')

    def test_no_matching_function(self):
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'len(1, 2, 3)')

    def test_mapping_translation_exception(self):
        self.context.register_function(
            lambda *args, **kwargs: 1, name='f')
        self.assertRaises(
            exceptions.MappingTranslationException,
            self.eval, 'f(2+2 => 4)')

    def test_no_matching_method(self):
        self.assertRaises(
            exceptions.NoMatchingMethodException,
            self.eval, '[1, 2].select(1, 2, 3)')

    def test_duplicate_parameters(self):
        def raises():
            @specs.parameter('p')
            @specs.parameter('p')
            def f(p):
                return p

        self.assertRaises(
            exceptions.DuplicateParameterDecoratorException,
            raises)

    def test_invalid_parameter(self):
        def raises():
            @specs.parameter('x')
            def f(p):
                return p

        self.assertRaises(
            exceptions.NoParameterFoundException,
            raises)

    def test_lexical_error(self):
        self.assertRaises(
            exceptions.YaqlLexicalException,
            self.eval, '1 ? 2')

    def test_grammar_error(self):
        self.assertRaises(
            exceptions.YaqlGrammarException,
            self.eval, '1 2')

        self.assertRaises(
            exceptions.YaqlGrammarException,
            self.eval, '(2')

    def test_invalid_method(self):
        self.assertRaises(
            exceptions.InvalidMethodException,
            self.context.register_function, lambda: 1, name='f', method=True)

        @specs.parameter('x', yaqltypes.Lambda())
        def func(x):
            return x

        self.assertRaises(
            exceptions.InvalidMethodException,
            self.context.register_function, func, name='f2', method=True)

    def test_function_definition(self):
        def func(a, b, *args, **kwargs):
            return a, b, args, kwargs

        fd = specs.get_function_definition(func)

        self.assertEqual(
            (1, 2, (5, 7), {'kw1': 'x', 'kw2': None}),
            fd(self.engine, self.context)(
                1, 2, 5, 7, kw1='x', kw2=None))

        self.assertEqual(
            (1, 5, (), {}),
            fd(self.engine, self.context)(1, b=5))

    def test_eval(self):
        self.assertEqual(
            120,
            yaql.eval(
                'let(inp => $) -> [1, 2, 3].select($ + $inp).reduce($1 * $2)',
                data=3)
        )

    def test_skip_args(self):
        def func(a=11, b=22, c=33):
            return a, b, c

        self.context.register_function(func)
        self.assertEqual([11, 22, 1], self.eval('func(,,1)'))
        self.assertEqual([0, 22, 1], self.eval('func(0,,1)'))
        self.assertEqual([11, 22, 33], self.eval('func()'))
        self.assertEqual([11, 1, 4], self.eval('func(,1, c=>4)'))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'func(,1, b=>4)')
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'func(,1,, c=>4)')

    def test_no_trailing_commas(self):
        self.assertRaises(exceptions.YaqlGrammarException,
                          self.eval, 'func(1,,)')
        self.assertRaises(exceptions.YaqlGrammarException,
                          self.eval, 'func(,1,)')
        self.assertRaises(exceptions.YaqlGrammarException,
                          self.eval, 'func(,,)')
        self.assertRaises(exceptions.YaqlGrammarException,
                          self.eval, 'func(,)')

    def test_no_varargs_after_kwargs(self):
        self.assertRaises(exceptions.YaqlGrammarException,
                          self.eval, 'func(x=>y, t)')
        self.assertRaises(exceptions.YaqlGrammarException,
                          self.eval, 'func(x=>y, ,t)')
        self.assertRaises(exceptions.YaqlGrammarException,
                          self.eval, 'func(a, x=>y, ,t)')

    def test_super(self):
        @specs.parameter('string', yaqltypes.String())
        @specs.inject('base', yaqltypes.Super())
        def len2(string, base):
            return 2 * base(string)

        context = self.context.create_child_context()
        context.register_function(len2, name='len')
        self.assertEqual(6, self.eval('len(abc)', context=context))

    def test_delegate_factory(self):
        @specs.parameter('name', yaqltypes.String())
        @specs.inject('__df__', yaqltypes.Delegate())
        def call_func(__df__, name, *args, **kwargs):
            return __df__(name, *args, **kwargs)

        context = self.context.create_child_context()

        context.register_function(call_func)
        self.assertEqual(
            [1, 2],
            self.eval('callFunc(list, 1, 2)', context=context))

        self.assertEqual(
            6,
            self.eval("callFunc('#operator_*', 2, 3)", context=context))

    def test_keyword_constant_function(self):
        @specs.parameter('arg', yaqltypes.Keyword())
        def foo(arg):
            return arg

        context = self.context.create_child_context()
        context.register_function(foo)

        self.assertEqual('qw', self.eval('foo(qw)', context=context))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo($)', context=context, data='asd')
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo("q w")', context=context)
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo(null)', context=context)

    def test_constant_function(self):
        @specs.parameter('arg', yaqltypes.Constant(True))
        def foo(arg):
            return arg

        context = self.context.create_child_context()
        context.register_function(foo)

        self.assertEqual('qw', self.eval('foo(qw)', context=context))
        self.assertEqual(123, self.eval('foo(123)', context=context))
        self.assertFalse(self.eval('foo(false)', context=context))
        self.assertIsNone(self.eval('foo(null)', context=context))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo($)', context=context, data='asd')

    def test_string_constant_function(self):
        @specs.parameter('arg', yaqltypes.StringConstant())
        def foo(arg):
            return arg

        context = self.context.create_child_context()
        context.register_function(foo)

        self.assertEqual('qw', self.eval('foo(qw)', context=context))
        self.assertEqual('q w', self.eval('foo("q w")', context=context))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo($)', context=context, data='asd')
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo(123)', context=context)
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo(null)', context=context)

    def test_numeric_constant_function(self):
        @specs.parameter('arg', yaqltypes.NumericConstant())
        def foo(arg):
            return arg

        context = self.context.create_child_context()
        context.register_function(foo)

        self.assertEqual(123, self.eval('foo(123)', context=context))
        self.assertEqual(12.4, self.eval('foo(12.4)', context=context))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo($)', context=context, data=5)
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo("123")', context=context)
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo(null)', context=context)

    def test_boolean_constant_function(self):
        @specs.parameter('arg', yaqltypes.BooleanConstant())
        def foo(arg):
            return arg

        context = self.context.create_child_context()
        context.register_function(foo)

        self.assertTrue(self.eval('foo(true)', context=context))
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo($)', context=context, data=True)
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo("true")', context=context)
        self.assertRaises(
            exceptions.NoMatchingFunctionException,
            self.eval, 'foo(null)', context=context)

    def test_high_precedence_operator_insertion(self):
        # Test that insertion of high precedence operator doesn't
        # make turn ($.a)[0] into $.(a[0])
        engine_factory = factory.YaqlFactory(allow_delegates=True)
        engine_factory.insert_operator(
            None, True, ':',
            factory.OperatorType.BINARY_LEFT_ASSOCIATIVE, True)
        engine = engine_factory.create()
        data = {'a': [1]}
        expr = engine('$.a[0]')
        self.assertEqual(1, expr.evaluate(context=self.context, data=data))
