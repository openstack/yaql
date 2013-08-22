#!/usr/bin/env python

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

import optparse
from json import JSONDecoder
import yaql
from yaql.cli import cli_functions


def main():
    p = optparse.OptionParser()
    p.add_option('--data', '-d')
    options, arguments = p.parse_args()
    if options.data:
        try:
            json_str = open(options.data).read()
            decoder = JSONDecoder()
            data = decoder.decode(json_str)
        except:
            print "Unable to load data from "+options.data
            return
    else:
        data = None

    context = yaql.create_context()
    cli_functions.register_in_context(context)
    yaql.parse('__main()').evaluate(data, context)


if __name__ == "__main__":
    main()
