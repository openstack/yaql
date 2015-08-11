#!/usr/bin/env python

#    Copyright (c) 2013-2015 Mirantis, Inc.
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

import json

import optparse

import yaql
from yaql.cli import cli_functions
import yaql.legacy


def main():
    p = optparse.OptionParser()
    p.add_option('--data', '-d')
    p.add_option('-t', action='store_true', dest='tokens')
    p.add_option('--legacy', action='store_true', dest='legacy')

    options, arguments = p.parse_args()
    if options.data:
        try:
            with open(options.data) as f:
                data = json.load(f)
        except Exception:
            print('Unable to load data from ' + options.data)
            return
    else:
        data = None

    engine_options = {
        'yaql.limitIterators': 100,
        'yaql.treatSetsAsLists': True,
        'yaql.memoryQuota': 10000
    }

    if options.legacy:
        factory = yaql.legacy.YaqlFactory()
        context = yaql.legacy.create_context()
        context['legacy'] = True
    else:
        factory = yaql.YaqlFactory()
        context = yaql.create_context()

    parser = factory.create(options=engine_options)
    cli_functions.register_in_context(context, parser)
    if options.tokens:
        parser('__main(true)').evaluate(data, context)
    else:
        parser('__main(false)').evaluate(data, context)


if __name__ == "__main__":
    main()
