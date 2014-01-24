#    Copyright (c) 2014 Mirantis, Inc.
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
from yaql.language.engine import context_aware, parameter
from yaql.language.exceptions import YaqlException


class NamespaceResolutionException(YaqlException):
    def __init__(self, alias):
        super(NamespaceResolutionException, self).__init__(
            "Unable to resolve namespace: %s" % alias)


class NamespaceValidationException(YaqlException):
    def __init__(self, name, symbol):
        super(NamespaceValidationException, self).__init__(
            "Namespace %s does not define %s" % (name, symbol))


class Namespace(object):
    def __init__(self, name, *symbols):
        self.name = name
        self.symbols = symbols

    def validate(self, symbol):
        if not symbol in self.symbols:
            raise NamespaceValidationException(self.name, symbol)


class NamespaceResolver(object):
    def __init__(self):
        self._ns = {}

    def register(self, alias, namespace):
        self._ns[alias] = namespace

    def resolve(self, alias):
        if alias in self._ns:
            return self._ns[alias]
        else:
            raise NamespaceResolutionException(alias)


@context_aware
@parameter('symbol', constant_only=True)
def resolve_prop(alias, symbol, context):
    resolver = get_resolver(context)
    namespace = resolver.resolve(alias)
    namespace.validate(symbol)
    return namespace.name + '.' + symbol

@context_aware
@parameter('symbol', function_only=True, lazy=True)
def resolve_function(self, alias, symbol, context):
    resolver = get_resolver(context)
    namespace = resolver.resolve(alias)
    namespace.validate(symbol.function_name)
    symbol.function_name = namespace.name + '.' + symbol.function_name
    return symbol(sender=self)


def add_to_context(context, resolver=None):
    context.set_data(resolver or NamespaceResolver(), '$__ns_resolver')
    context.register_function(resolve_prop, 'operator_:')
    context.register_function(resolve_function, 'operator_:')


def get_resolver(context):
    return context.get_data('$__ns_resolver')
