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
import examples.ns.definition
from yaql.functions.old.decorators import arg


@arg('short_name', type=types.StringType)
@arg('value', type=types.StringType)
def expand_property_namespace(short_name, value):
    fqns = examples.ns.definition.get_fqns(short_name)
    if not fqns:
        raise Exception(
            "Namespace with alias '{0}' is unknown".format(short_name))
    if not examples.ns.definition.validate(fqns, value):
        raise Exception(
            "Namespace '{0}' does not contain name '{1}'".format(fqns, value))
    return "{0}.{1}".format(fqns, value)

@arg('short_name', type=types.StringType)
@arg('value', eval_arg=False, function_only=True)
def expand_function_namespace(short_name, value):
    fqns = examples.ns.definition.get_fqns(short_name)
    if not fqns:
        raise Exception(
            "Namespace with alias '{0}' is unknown".format(short_name))
    if not examples.ns.definition.validate(fqns, value.function_name):
        raise Exception(
            "Namespace '{0}' does not contain name '{1}'".format(fqns, value))
    value.function_name = "{0}.{1}".format(fqns, value.function_name)
    return value



def register_in_context(context):
    context.register_function(expand_property_namespace, 'operator_:')
    context.register_function(expand_function_namespace, 'operator_:')

