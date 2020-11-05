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

import abc

import six

from yaql.language import exceptions
from yaql.language import runner
from yaql.language import specs
from yaql.language import utils


@six.add_metaclass(abc.ABCMeta)
class ContextBase(object):
    def __init__(self, parent_context=None, convention=None):
        """
        Initialize the context.

        Args:
            self: (todo): write your description
            parent_context: (todo): write your description
            convention: (todo): write your description
        """
        self._parent_context = parent_context
        self._convention = convention
        if convention is None and parent_context:
            self._convention = parent_context.convention

    @property
    def parent(self):
        """
        Return the parent. parent.

        Args:
            self: (todo): write your description
        """
        return self._parent_context

    @abc.abstractmethod
    def register_function(self, spec, *args, **kwargs):
        """
        Register a function.

        Args:
            self: (todo): write your description
            spec: (todo): write your description
        """
        pass

    @abc.abstractmethod
    def get_data(self, name, default=None, ask_parent=True):
        """
        Get the data for a given name.

        Args:
            self: (todo): write your description
            name: (str): write your description
            default: (bool): write your description
            ask_parent: (str): write your description
        """
        return default

    def __getitem__(self, name):
        """
        Return the value from the cache.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        return self.get_data(name)

    @abc.abstractmethod
    def __setitem__(self, name, value):
        """
        Sets a value of the given name.

        Args:
            self: (todo): write your description
            name: (str): write your description
            value: (str): write your description
        """
        pass

    @abc.abstractmethod
    def __delitem__(self, name):
        """
        Removes an item

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        pass

    @abc.abstractmethod
    def __contains__(self, item):
        """
        Determine if item is contained in the list.

        Args:
            self: (todo): write your description
            item: (str): write your description
        """
        return False

    def __call__(self, name, engine, receiver=utils.NO_VALUE,
                 data_context=None, use_convention=False,
                 function_filter=None):
        """
        Call a call on a call arguments.

        Args:
            self: (todo): write your description
            name: (str): write your description
            engine: (todo): write your description
            receiver: (str): write your description
            utils: (todo): write your description
            NO_VALUE: (str): write your description
            data_context: (todo): write your description
            use_convention: (bool): write your description
            function_filter: (todo): write your description
        """
        return lambda *args, **kwargs: runner.call(
            name, self, args, kwargs, engine, receiver,
            data_context, use_convention, function_filter)

    @abc.abstractmethod
    def get_functions(self, name, predicate=None, use_convention=False):
        """
        Returns a list of all of the given name.

        Args:
            self: (todo): write your description
            name: (str): write your description
            predicate: (str): write your description
            use_convention: (todo): write your description
        """
        return [], False

    @abc.abstractmethod
    def delete_function(self, spec):
        """
        Delete a function.

        Args:
            self: (todo): write your description
            spec: (todo): write your description
        """
        pass

    def collect_functions(self, name, predicate=None, use_convention=False):
        """
        Returns a list of functions for a context.

        Args:
            self: (todo): write your description
            name: (str): write your description
            predicate: (bool): write your description
            use_convention: (bool): write your description
        """
        overloads = []
        p = self
        while p is not None:
            context_predicate = None
            if predicate:
                context_predicate = lambda fd: predicate(fd, p)  # noqa: E731
            layer_overloads, is_exclusive = p.get_functions(
                name, context_predicate, use_convention)
            p = None if is_exclusive else p.parent
            if layer_overloads:
                overloads.append(layer_overloads)
        return overloads

    def create_child_context(self):
        """
        Create a new child context.

        Args:
            self: (todo): write your description
        """
        return type(self)(self)

    @property
    def convention(self):
        """
        Convention. convention.

        Args:
            self: (todo): write your description
        """
        return self._convention

    @abc.abstractmethod
    def keys(self):
        """
        Return a list of all keys.

        Args:
            self: (todo): write your description
        """
        return six.iterkeys({})


class Context(ContextBase):
    def __init__(self, parent_context=None, data=utils.NO_VALUE,
                 convention=None):
        """
        Initialize the context.

        Args:
            self: (todo): write your description
            parent_context: (todo): write your description
            data: (todo): write your description
            utils: (todo): write your description
            NO_VALUE: (todo): write your description
            convention: (todo): write your description
        """
        super(Context, self).__init__(parent_context, convention)
        self._functions = {}
        self._data = {}
        self._exclusive_funcs = set()
        if data is not utils.NO_VALUE:
            self['$'] = data

    @staticmethod
    def _import_function_definition(fd):
        """
        Import a function definition.

        Args:
            fd: (todo): write your description
        """
        return fd

    def register_function(self, spec, *args, **kwargs):
        """
        Register a function.

        Args:
            self: (todo): write your description
            spec: (todo): write your description
        """
        exclusive = kwargs.pop('exclusive', False)

        if not isinstance(spec, specs.FunctionDefinition) \
                and six.callable(spec):
            spec = specs.get_function_definition(
                spec, *args, convention=self._convention, **kwargs)

        spec = self._import_function_definition(spec)
        if spec.is_method:
            if not spec.is_valid_method():
                raise exceptions.InvalidMethodException(spec.name)
        self._functions.setdefault(spec.name, set()).add(spec)
        if exclusive:
            self._exclusive_funcs.add(spec.name)

    def delete_function(self, spec):
        """
        Removes a function.

        Args:
            self: (todo): write your description
            spec: (todo): write your description
        """
        self._functions.get(spec.name, set()).discard(spec)
        self._exclusive_funcs.discard(spec.name)

    def get_functions(self, name, predicate=None, use_convention=False):
        """
        Returns a list of all the functions.

        Args:
            self: (todo): write your description
            name: (str): write your description
            predicate: (str): write your description
            use_convention: (todo): write your description
        """
        name = name.rstrip('_')
        if use_convention and self._convention is not None:
            name = self._convention.convert_function_name(name)
        if predicate is None:
            predicate = lambda x: True  # noqa: E731
        return (
            set(six.moves.filter(predicate, self._functions.get(name, set()))),
            name in self._exclusive_funcs
        )

    @staticmethod
    def _normalize_name(name):
        """
        Normalize name.

        Args:
            name: (str): write your description
        """
        if not name.startswith('$'):
            name = ('$' + name)
        if name == '$':
            name = '$1'
        return name

    def __setitem__(self, name, value):
        """
        Sets an item.

        Args:
            self: (todo): write your description
            name: (str): write your description
            value: (str): write your description
        """
        self._data[self._normalize_name(name)] = value

    def get_data(self, name, default=None, ask_parent=True):
        """
        Get a value from the context.

        Args:
            self: (todo): write your description
            name: (str): write your description
            default: (bool): write your description
            ask_parent: (str): write your description
        """
        name = self._normalize_name(name)
        if name in self._data:
            return self._data[name]
        ctx = self.parent
        while ask_parent and ctx:
            result = ctx.get_data(name, utils.NO_VALUE, False)
            if result is utils.NO_VALUE:
                ctx = ctx.parent
            else:
                return result
        return default

    def __delitem__(self, name):
        """
        Remove an item from the list.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        self._data.pop(self._normalize_name(name))

    def __contains__(self, item):
        """
        Returns true if item contains a given item.

        Args:
            self: (todo): write your description
            item: (str): write your description
        """
        if isinstance(item, specs.FunctionDefinition):
            return item in self._functions.get(item.name, [])
        if isinstance(item, six.string_types):
            return self._normalize_name(item) in self._data
        return False

    def keys(self):
        """
        Returns a list of the keys.

        Args:
            self: (todo): write your description
        """
        return six.iterkeys(self._data)


class MultiContext(ContextBase):
    def __init__(self, context_list, convention=None):
        """
        Initialize the context.

        Args:
            self: (todo): write your description
            context_list: (list): write your description
            convention: (todo): write your description
        """
        self._context_list = context_list
        if convention is None:
            convention = context_list[0].convention
        parents = tuple(six.moves.filter(
            lambda t: t,
            six.moves.map(lambda t: t.parent, context_list)))
        if not parents:
            super(MultiContext, self).__init__(None, convention)
        elif len(parents) == 1:
            super(MultiContext, self).__init__(parents[0], convention)
        else:
            super(MultiContext, self).__init__(MultiContext(parents),
                                               convention)

    def register_function(self, spec, *args, **kwargs):
        """
        Register a function.

        Args:
            self: (todo): write your description
            spec: (todo): write your description
        """
        self._context_list[0].register_function(spec, *args, **kwargs)

    def get_data(self, name, default=None, ask_parent=True):
        """
        Get a value from the context.

        Args:
            self: (todo): write your description
            name: (str): write your description
            default: (bool): write your description
            ask_parent: (str): write your description
        """
        for context in self._context_list:
            result = context.get_data(name, utils.NO_VALUE, False)
            if result is not utils.NO_VALUE:
                return result
        ctx = self.parent
        while ask_parent and ctx:
            result = ctx.get_data(name, utils.NO_VALUE, False)
            if result is utils.NO_VALUE:
                ctx = ctx.parent
            else:
                return result
        return default

    def __setitem__(self, name, value):
        """
        Creates a new context variable.

        Args:
            self: (todo): write your description
            name: (str): write your description
            value: (str): write your description
        """
        self._context_list[0][name] = value

    def __delitem__(self, name):
        """
        Removes an item from context.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        for context in self._context_list:
            del context[name]

    def create_child_context(self):
        """
        Create a new context context.

        Args:
            self: (todo): write your description
        """
        return Context(self)

    def keys(self):
        """
        Return an iterable of ( key / values.

        Args:
            self: (todo): write your description
        """
        prev_keys = set()
        for context in self._context_list:
            for key in context.keys():
                if key not in prev_keys:
                    prev_keys.add(key)
                    yield key

    def delete_function(self, spec):
        """
        Removes a function from the context.

        Args:
            self: (todo): write your description
            spec: (todo): write your description
        """
        for context in self._context_list:
            context.delete_function(spec)

    def __contains__(self, item):
        """
        Return true if item is contained items.

        Args:
            self: (todo): write your description
            item: (str): write your description
        """
        for context in self._context_list:
            if item in context:
                return True
        return False

    def get_functions(self, name, predicate=None, use_convention=False):
        """
        Returns a list of all the functions.

        Args:
            self: (todo): write your description
            name: (str): write your description
            predicate: (str): write your description
            use_convention: (todo): write your description
        """
        result = set()
        is_exclusive = False
        for context in self._context_list:
            funcs, exclusive = context.get_functions(
                name, predicate, use_convention)
            result.update(funcs)
            if exclusive:
                is_exclusive = True
        return result, is_exclusive


class LinkedContext(ContextBase):
    """Context that is as a proxy to another context but has its own parent."""

    def __init__(self, parent_context, linked_context, convention=None):
        """
        Initialize the context.

        Args:
            self: (todo): write your description
            parent_context: (todo): write your description
            linked_context: (todo): write your description
            convention: (todo): write your description
        """
        self.linked_context = linked_context
        if linked_context.parent:
            super(LinkedContext, self).__init__(
                LinkedContext(parent_context, linked_context.parent,
                              convention), convention)
        else:
            super(LinkedContext, self).__init__(parent_context, convention)

    def register_function(self, spec, *args, **kwargs):
        """
        Registers a context manager.

        Args:
            self: (todo): write your description
            spec: (todo): write your description
        """
        return self.linked_context.register_function(spec, *args, **kwargs)

    def keys(self):
        """
        Returns a list of all keys. : rdf.

        Args:
            self: (todo): write your description
        """
        return self.linked_context.keys()

    def get_data(self, name, default=None, ask_parent=True):
        """
        Return the data for the named category.

        Args:
            self: (todo): write your description
            name: (str): write your description
            default: (bool): write your description
            ask_parent: (str): write your description
        """
        result = self.linked_context.get_data(
            name, default=utils.NO_VALUE, ask_parent=False)
        if result is utils.NO_VALUE:
            if not ask_parent or not self.parent:
                return default
            return self.parent.get_data(name, default=default, ask_parent=True)
        return result

    def get_functions(self, name, predicate=None, use_convention=False):
        """
        Retrieves a list of all matching name.

        Args:
            self: (todo): write your description
            name: (str): write your description
            predicate: (str): write your description
            use_convention: (todo): write your description
        """
        return self.linked_context.get_functions(
            name, predicate=predicate, use_convention=use_convention)

    def delete_function(self, spec):
        """
        Delete a function from the context.

        Args:
            self: (todo): write your description
            spec: (todo): write your description
        """
        return self.linked_context.delete_function(spec)

    def __contains__(self, item):
        """
        Determine if item is contained item.

        Args:
            self: (todo): write your description
            item: (str): write your description
        """
        return item in self.linked_context

    def __delitem__(self, name):
        """
        Removes an item from the context.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        del self.linked_context[name]

    def __setitem__(self, name, value):
        """
        Sets a new value of a given name.

        Args:
            self: (todo): write your description
            name: (str): write your description
            value: (str): write your description
        """
        self.linked_context[name] = value

    def create_child_context(self):
        """
        Create a new child context.

        Args:
            self: (todo): write your description
        """
        return type(self.linked_context)(self)
