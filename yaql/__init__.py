import parser
import context
from yaql.functions import builtin, extended


def parse(expression):
    return parser.parse(expression)


def create_context(include_extended_functions=True):
    cont = context.Context()
    builtin.add_to_context(cont)
    if include_extended_functions:
        extended.add_to_context(cont)
    return context.Context(cont)

