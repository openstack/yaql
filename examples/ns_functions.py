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
from yaql.context import EvalArg


@EvalArg('short_name', arg_type=types.StringType)
def expand_namespace(short_name):
    fqns = examples.ns.definition.get_fqns(short_name)
    if not fqns:
        raise Exception(
            "Namespace with alias '{0}' is unknown".format(short_name))
    else:
        return fqns


@EvalArg('fqns', arg_type=types.StringType)
@EvalArg('value', arg_type=types.StringType)
def validate(fqns, value):
    if not examples.ns.definition.validate(fqns, value):
        raise Exception(
            "Namespace '{0}' does not contain name '{1}'".format(fqns, value))
    return "{0}.{1}".format(fqns, value)


def register_in_context(context):
    context.register_function(expand_namespace, 'operator_:')
    context.register_function(validate, 'validate')
