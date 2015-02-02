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

from yaql.language import specs
from yaql.language import yaqltypes


@specs.parameter('args', yaqltypes.MappingRule())
@specs.no_kwargs
def switch(*args):
    for mapping in args:
        if mapping.source():
            return mapping.destination()


@specs.parameter('args', yaqltypes.Lambda())
def select_case(*args):
    index = 0
    for f in args:
        if f():
            return index
        index += 1
    return index


@specs.parameter('args', yaqltypes.Lambda())
def select_all_cases(*args):
    for i, f in enumerate(args):
        if f():
            yield i


@specs.parameter('args', yaqltypes.Lambda())
def examine(*args):
    for f in args:
        yield bool(f())


@specs.parameter('case', int)
@specs.parameter('args', yaqltypes.Lambda())
@specs.method
def switch_case(case, *args):
    if 0 <= case < len(args):
        return args[case]()
    if len(args) == 0:
        return None
    return args[-1]()


@specs.parameter('args', yaqltypes.Lambda())
def coalesce(*args):
    for f in args:
        res = f()
        if res is not None:
            return res
    return None


def register(context):
    context.register_function(switch)
    context.register_function(select_case)
    context.register_function(switch_case)
    context.register_function(select_all_cases)
    context.register_function(examine)
    context.register_function(coalesce)
