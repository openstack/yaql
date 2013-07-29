import types
import ns.definition
from yaql.context import EvalArg


@EvalArg('short_name', arg_type=types.StringType)
def expand_namespace(short_name):
    fqns = ns.definition.get_fqns(short_name)
    if not fqns:
        raise Exception(
            "Namespace with alias '{0}' is unknown".format(short_name))
    else:
        return fqns


@EvalArg('fqns', arg_type=types.StringType)
@EvalArg('value', arg_type=types.StringType)
def validate(fqns, value):
    if not ns.definition.validate(fqns, value):
        raise Exception(
            "Namespace '{0}' does not contain name '{1}'".format(fqns, value))
    return "{0}.{1}".format(fqns, value)


def register_in_context(context):
    context.register_function(expand_namespace, 'operator_:')
    context.register_function(validate, 'validate')
