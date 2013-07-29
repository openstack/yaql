short_names = {}
values = {}


def register_shortening(short_name, fqns):
    existing = short_names.get(short_name)
    if existing and existing != fqns:
        raise Exception(
            "A namespace ('{0}') is already registered as '{1}'".format(
                existing, short_name))
    short_names[short_name] = fqns


def register_symbol(fqns, symbol):
    if not fqns in values:
        values[fqns] = {symbol}
    else:
        values[fqns].add(symbol)


def get_fqns(short_name):
    return short_names.get(short_name)


def validate(fqns, value):
    return fqns in values and value in values[fqns]