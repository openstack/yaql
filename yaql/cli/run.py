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
import sys

import yaql
from yaql.cli import cli_functions
import yaql.legacy


def read_data(f, options):
    if options.string:
        if options.array:
            return [line.rstrip('\n') for line in f]
        else:
            return f.read()
    else:
        if options.array:
            return [json.loads(s) for s in f.readlines()]
        else:
            return json.load(f)


def main():
    p = optparse.OptionParser()
    p.add_option('--data', '-d', help="input file")
    p.add_option('--string', '-s', action='store_true',
                 help="input is a string")
    p.add_option('--native', '-n', action='store_true',
                 help="output data in Python native format")
    p.add_option('--array', '-a', action='store_true',
                 help="read input line by line")
    p.add_option('--tokens', '-t', action='store_true', dest='tokens',
                 help="print lexical tokens info")
    p.add_option('--legacy', '-l', action='store_true', dest='legacy',
                 help="enable legacy v0.2 compatibility mode")
    p.add_option('--limit', '--limit-iterators', '-L', type=int,
                 dest='limit_iterators',
                 default=1000, help="limit iterators by the given number of "
                                    "elements (-1 means infinity)")
    p.add_option('--sets-to-lists', '-S', action="store_true",
                 dest='sets_to_lists', default=True,
                 help="convert all sets in results to lists")
    p.add_option('--tuples-to-lists', '-T', action="store_true",
                 dest='tuples_to_lists', default=False,
                 help="convert all tuples in results to lists")
    p.add_option('--iterable-dicts', '-D', action="store_true",
                 dest='iterable_dicts', default=False,
                 help="consider dictionaries to be iterable over their keys")
    p.add_option('--memory-quota', '--mem', '-m', type=int, dest='memory',
                 default=100000, help="change memory usage quota (in bytes) "
                                      "for all data produced by expressions "
                                      "(-1 means infinity)")
    p.add_option('--keyword-operator', '-k', type=str, dest='keyword_operator',
                 default="=>", help="configure keyword/mapping symbol "
                                    "(empty string means disabled)")
    p.add_option('--allow-delegates', '-A', action="store_true",
                 dest='allow_delegates', default=False,
                 help="enable delegate expression parsing")

    options, arguments = p.parse_args()
    if options.data:
        try:
            if options.data == '-':
                data = read_data(sys.stdin, options)
            else:
                with open(options.data) as f:
                    data = read_data(f, options)
        except Exception:
            print('Unable to load data from ' + options.data, file=sys.stderr)
            exit(1)
    else:
        data = None

    engine_options = {
        'yaql.limitIterators': options.limit_iterators,
        'yaql.convertSetsToLists': options.sets_to_lists,
        'yaql.convertTuplesToLists': options.tuples_to_lists,
        'yaql.iterableDicts': options.iterable_dicts,
        'yaql.memoryQuota': options.memory
    }

    if options.legacy:
        factory = yaql.legacy.YaqlFactory(
            allow_delegates=options.allow_delegates
        )
        context = yaql.legacy.create_context()
        context['legacy'] = True
    else:
        factory = yaql.YaqlFactory(
            allow_delegates=options.allow_delegates,
            keyword_operator=options.keyword_operator
        )
        context = yaql.create_context()

    if options.native:
        context['#nativeOutput'] = True

    parser = factory.create(options=engine_options)
    cli_functions.register_in_context(context, parser)

    if len(arguments) > 0:
        for arg in arguments:
            cli_functions.evaluate(arg, parser, data, context)
    elif options.tokens:
        parser('__main(true)').evaluate(data, context)
    else:
        parser('__main(false)').evaluate(data, context)


if __name__ == "__main__":
    main()
