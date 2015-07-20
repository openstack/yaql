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
    def __init__(self, parent_context=None, convention=None):
        self._parent_context = parent_context
        self._convention = convention
        if convention is None and parent_context:
            self._convention = parent_context.convention

    @property
    def parent(self):
        return self._parent_context

    def register_function(self, spec, *args, **kwargs):
        pass

    def get_data(self, name, default=None, ask_parent=True):
        return default

    def __getitem__(self, name):
        return self.get_data(name)

    def __setitem__(self, name, value):
        pass

    def __delitem__(self, name):
        pass

    def __contains__(self, item):
        return self.get_data(item, utils.NO_VALUE) is not utils.NO_VALUE

    def __call__(self, name, engine, sender=utils.NO_VALUE,
                 data_context=None, use_convention=False,
                 function_filter=None):
        return lambda *args, **kwargs: runner.call(
            name, self, args, kwargs, engine, sender,
            data_context, use_convention, function_filter)

    def get_functions(self, name, predicate=None, use_convention=False):
        return []

    def collect_functions(self, name, predicate=None, use_convention=False):
        return [[]]

    def create_child_context(self):
        return type(self)(self)

    @property
    def convention(self):
        return self._convention


class Context(ContextBase):
    def __init__(self, parent_context=None, data=utils.NO_VALUE,
                 convention=None):
        super(Context, self).__init__(parent_context, convention)
        self._functions = {}
        self._data = {}
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
        name = name.rstrip('_')
        if use_convention and self._convention is not None:
            name = self._convention.convert_function_name(name)
        if predicate is None:
            predicate = lambda x: True
        return six.moves.filter(predicate, list(six.moves.map(
            lambda x: x[0],
            self._functions.get(name, list()))))

    def collect_functions(self, name, predicate=None, use_convention=False):
        name = name.rstrip('_')
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
                    if predicate and not predicate(spec, self):
                        continue
                    layer.append(spec)
                if layer:
                    overloads.append(layer)
        return overloads

    @staticmethod
    def _normalize_name(name):
        if not name.startswith('$'):
            name = ('$' + name)
        if name == '$':
            name = '$1'
        return name

    def __setitem__(self, name, value):
        self._data[self._normalize_name(name)] = value

    def get_data(self, name, default=None, ask_parent=True):
        name = self._normalize_name(name)
        if name in self._data:
            return self._data[name]
        if self.parent and ask_parent:
            return self.parent.get_data(name, default, ask_parent)
        return default

    def __delitem__(self, name):
        self._data.pop(self._normalize_name(name))

    def create_child_context(self):
        return Context(self, convention=self._convention)


class MultiContext(ContextBase):
    def __init__(self, context_list, convention=None):
        self._context_list = context_list
        if convention is None:
            convention = context_list[0].convention
        parents = six.moves.filter(
            lambda t: t,
            six.moves.map(lambda t: t.parent, context_list))
        if not parents:
            super(MultiContext, self).__init__(None, convention)
        elif len(parents) == 1:
            super(MultiContext, self).__init__(parents[0], convention)
        else:
            super(MultiContext, self).__init__(MultiContext(parents),
                                               convention)

    def register_function(self, spec, *args, **kwargs):
        self._context_list[0].register_function(spec, *args, **kwargs)

    def get_data(self, name, default=None, ask_parent=True):
        for context in self._context_list:
            result = context.get_data(name, utils.NO_VALUE, False)
            if result is not utils.NO_VALUE:
                return result
        if ask_parent and self.parent:
            return self.parent.get_data(name, default, ask_parent)
        return default

    def __setitem__(self, name, value):
        self._context_list[0][name] = value

    def get_functions(self, name, predicate=None, use_convention=False):
        result = []
        for context in self._context_list:
            result.extend(context.get_functions(
                name, predicate, use_convention))
        return result

    def collect_functions(self, name, predicate=None, use_convention=False):
        functions = six.moves.map(
            lambda ctx: ctx.collect_functions(name, predicate, use_convention),
            self._context_list)
        i = 0
        result = []
        while True:
            level = []
            has_level = False
            for f in functions:
                if len(f) > i:
                    has_level = True
                    level.extend(f[i])
            if not has_level:
                return result
            i += 1
            result.append(level)

    def __delitem__(self, name):
        for context in self._context_list:
            del context[name]

    def create_child_context(self):
        return Context(self)
