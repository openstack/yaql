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