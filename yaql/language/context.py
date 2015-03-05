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

import six

from yaql.language import exceptions
from yaql.language import runner
from yaql.language import specs
from yaql.language import utils


class ContextBase(object):
    def __init__(self, parent_context):
        self._parent_context = parent_context

    @property
    def parent(self):
        return self._parent_context

    def register_function(self, spec, *args, **kwargs):
        pass

    def __getitem__(self, name):
        return None

    def __setitem__(self, name, value):
        pass

    def __delitem__(self, name):
        pass

    def __call__(self, name, engine, sender=utils.NO_VALUE,
                 data_context=None, return_context=False,
                 use_convention=False):
        raise exceptions.NoFunctionRegisteredException(name)

    def get_functions(self, name, predicate=None, use_convention=False):
        return []

    def collect_functions(self, name, predicate=None, use_convention=False):
        return [[]]

    def create_child_context(self):
        return type(self)(self)


class Context(ContextBase):
    def __init__(self, parent_context=None, data=utils.NO_VALUE,
                 convention=None):
        super(Context, self).__init__(parent_context)
        self._functions = {}
        self._data = {}
        self._convention = convention
        if data is not utils.NO_VALUE:
            self['$'] = data

    @staticmethod
    def _import_function_definition(fd):
        return fd

    def register_function(self, spec, *args, **kwargs):
        exclusive = kwargs.pop('exclusive', False)

        if not isinstance(spec, specs.FunctionDefinition) \
                and six.callable(spec):
            spec = specs.get_function_definition(
                spec, *args, convention=self._convention, **kwargs)

        spec = self._import_function_definition(spec)
        if spec.is_method:
            if not spec.is_valid_method():
                raise exceptions.InvalidMethodException(spec.name)
        self._functions.setdefault(spec.name, list()).append((spec, exclusive))

    def get_functions(self, name, predicate=None, use_convention=False):
        if use_convention and self._convention is not None:
            name = self._convention.convert_function_name(name)
        if predicate is None:
            predicate = lambda x: True
        return six.moves.filter(predicate, list(six.moves.map(
            lambda x: x[0],
            self._functions.get(name, list()))))

    def collect_functions(self, name, predicate=None, use_convention=False):
        if use_convention and self._convention is not None:
            name = self._convention.convert_function_name(name)
        overloads = []
        p = self
        while p is not None:
            layer_overloads = p._functions.get(name)
            p = p.parent
            if layer_overloads:
                layer = []
                for spec, exclusive in layer_overloads:
                    if exclusive:
                        p = None
                    if predicate and not predicate(spec):
                        continue
                    layer.append(spec)
                if layer:
                    overloads.append(layer)
        return overloads

    def __call__(self, name, engine, sender=utils.NO_VALUE,
                 data_context=None, return_context=False,
                 use_convention=False):
        return lambda *args, **kwargs: runner.call(
            name, self, args, kwargs, engine, sender,
            data_context, return_context, use_convention)

    @staticmethod
    def _normalize_name(name):
        if not name.startswith('$'):
            name = ('$' + name)
        if name == '$':
            name = '$1'
        return name

    def __setitem__(self, name, value):
        self._data[self._normalize_name(name)] = value

    def __getitem__(self, name):
        name = self._normalize_name(name)
        if name in self._data:
            return self._data[name]
        if self.parent:
            return self.parent[name]

    def __delitem__(self, name):
        self._data.pop(self._normalize_name(name))

    def create_child_context(self):
        return Context(self, convention=self._convention)
