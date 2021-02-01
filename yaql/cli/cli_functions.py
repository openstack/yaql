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
import os
import readline
import sys

from yaql import __version__ as version
from yaql.language.exceptions import YaqlParsingException
from yaql.language import utils


PROMPT = "yaql> "


def main(context, show_tokens, parser):
    print("Yet Another Query Language - command-line query tool")
    print("Version {0}".format(version))
    if context.get_data('legacy', False):
        print("Running in a legacy (0.2.x compatible) mode")
    print("Copyright (c) 2013-2017 Mirantis, Inc")
    print("")
    if not context['']:
        print("No data loaded into context ")
        print("Type '@load data-file.json' to load data")
        print("")

    readline.parse_and_bind('')

    comm = True
    while comm != 'exit':
        try:
            comm = input(PROMPT)
        except EOFError:
            return
        if not comm:
            continue
        if comm[0] == '@':
            func_name, args = parse_service_command(comm)
            if func_name not in SERVICE_FUNCTIONS:
                print('Unknown command ' + func_name)
            else:
                SERVICE_FUNCTIONS[func_name](args, context)
            continue
        try:
            if show_tokens:
                parser.lexer.input(comm)
                tokens = []
                while True:
                    tok = parser.lexer.token()
                    if not tok:
                        break
                    tokens.append(tok)
                print('Tokens: ' + str(tokens))
            expr = parser(comm)
            if show_tokens:
                print('Expression: ' + str(expr))

        except YaqlParsingException as ex:
            if ex.position:
                pointer_string = (" " * (ex.position + len(PROMPT))) + '^'
                print(pointer_string)
            print(ex.message)
            continue
        try:
            res = expr.evaluate(context=context)
            print_output(res, context)
        except Exception as ex:
            print(u'Execution exception: {0}'.format(ex), file=sys.stderr)


def load_data(data_file, context):
    try:
        json_str = open(os.path.expanduser(data_file)).read()
    except IOError as e:
        print("Unable to read data file '{0}': {1}".format(data_file,
                                                           e.strerror))
        return
    try:
        data = json.loads(json_str)
    except Exception as e:
        print('Unable to parse data: ' + e.message)
        return
    context['$'] = utils.convert_input_data(data)
    print('Data from file {0} loaded into context'.format(data_file))


def register_in_context(context, parser):
    context.register_function(
        lambda context, show_tokens: main(context, show_tokens, parser),
        name='__main')


def parse_service_command(comm):
    space_index = comm.find(' ')
    if space_index == -1:
        return comm, None
    func_name = comm[:space_index]
    args = comm[len(func_name) + 1:]
    return func_name, args


def evaluate(expr, parser, data, context):
    try:
        res = parser(expr).evaluate(data, context)
        print_output(res, context)
    except Exception as ex:
        print(u'Execution exception: {0}'.format(ex), file=sys.stderr)
        exit(1)


def print_output(v, context):
    if context['#nativeOutput']:
        print(v)
    else:
        print(json.dumps(v, indent=4, ensure_ascii=False))


SERVICE_FUNCTIONS = {
    # '@help':print_help,
    '@load': load_data,
    # '@import':import_module,
    # '@register':register_function
}
