#    Copyright (c) 2016 Mirantis, Inc.
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

import argparse
import importlib
import operator
import pkgutil
import sys
import types


TAG = ':yaql:'


def _get_name(module):
    """Get name of the module in the library directory"""

    name_stub = module.__name__.split('.')
    name = name_stub[-1].capitalize()

    return name


def _get_modules_names(package):
    """Get names of modules in package"""

    for _, name, _ in pkgutil.walk_packages(package.__path__,
                                            '{0}.'.format(package.__name__)):
        yield name


def _get_functions_names(module):
    """Get names of the functions in the current module"""

    return [name for name in dir(module) if
            isinstance(getattr(module, name, None),
                       types.FunctionType)]


def _construct_method_docs(method):
    """Construct method documentation from a docstring.

    1) Strip TAG
    2) Embolden function name
    3) Add :callAs: after :signature:
    """

    msg = "Function {0} has no valid YAQL documentation."

    if method.__doc__:
        doc = method.__doc__
        try:
            # strip TAG
            doc = doc[doc.index(TAG) + len(TAG):]

            # embolden function name
            line_break = doc.index('\n')
            doc = '**{0}**{1}'.format(doc[:line_break], doc[line_break:])

            # add :callAs: parameter
            signature_index = doc.index(':signature:')
            position = doc.index('    :', signature_index +
                                 len(':signature:'))

            if hasattr(method, '__yaql_function__'):
                if (method.__yaql_function__.name and
                        'operator' in method.__yaql_function__.name):
                    call_as = 'operator'
                elif (method.__yaql_function__.is_function and
                        method.__yaql_function__.is_method):
                    call_as = 'function or method'
                elif method.__yaql_function__.is_method:
                    call_as = 'method'
                else:
                    call_as = 'function'
            else:
                call_as = 'function'

            call_as_str = '    :callAs: {0}\n'.format(call_as)
            return doc[:position] + call_as_str + doc[position:]
        except ValueError:
            return msg.format(method.func_name)


def _get_functions_docs(module):
    """Collect YAQL docstrings.

    Collect functions docstrings after TAG.
    """
    functions_names = _get_functions_names(module)
    if module.__doc__:
        docs_list = [module.__doc__]
        func_docs_list = []
        for name in functions_names:
            method = getattr(module, name)
            method_docs = _construct_method_docs(method)
            if method_docs:
                func_docs_list.append('\n{0}\n'.format(method_docs))
        func_docs_list.sort()
        docs_list.extend(func_docs_list)
    else:
        docs_list = ['\nModule is not documented yet']
    return docs_list


def _add_markup(obj):
    body = ''
    subtitle = '{0} functions\n'.format(obj['module_name'])
    markup = '{0}\n'.format('~' * (len(subtitle) - 1))
    body = ''.join(obj['documentation'])
    return '{0}{1}{2}\n\n'.format(subtitle, markup, body)


def _write_to_doc(output, header, stub):
    if header:
        output.write("{0}\n{1}\n\n".format(header,
                                           '=' * len(header)))
    sorted_stub = sorted(stub, key=operator.itemgetter('module_name'))
    for elem in sorted_stub:
        if elem:
            markuped = _add_markup(elem)
            output.write(markuped)


def generate_doc_for_module(module, output):
    """Generate and write rst document for module.

    Generate and write rst document for the single module. By default it will
    print to stdout.

    :parameter module: takes a Python module which should be documented.
    :type module: Python module

    :parameter output: takes file to which generated document will be written.
    :type output: file
    """
    doc_stub = []
    docs_for_module = _get_functions_docs(module)
    doc_dict = {'module_name': _get_name(module),
                'documentation': docs_for_module}
    doc_stub.append(doc_dict)
    doc_name = module.__name__.rsplit('.', 1)[-1]
    doc_header = doc_name.replace("_", " ").capitalize()
    _write_to_doc(output, doc_header, doc_stub)


def generate_doc_for_package(package, output, no_header):
    """Generate and write rst document for package.

    Generate and write rst document for the modules in the given package. By
    default it will print to stdout.

    :parameter package: takes a Python package which should be documented
    :type package: Python module

    :parameter output: takes file to which generated document will be written.
    :type output: file
    """

    modules = _get_modules_names(package)
    doc_stub = []
    for module_name in modules:
        current_module = importlib.import_module(module_name)
        docs_for_module = _get_functions_docs(current_module)
        doc_dict = {'module_name': _get_name(current_module),
                    'documentation': docs_for_module}
        doc_stub.append(doc_dict)
    if no_header:
        doc_header = None
    else:
        doc_name = package.__name__.rsplit('.', 1)[-1]
        doc_header = doc_name.replace("_", " ").capitalize()
    _write_to_doc(output, doc_header, doc_stub)


def main(args):
    try:
        package = importlib.import_module(args.package)
    except ImportError:
        raise ValueError("No such package {0}".format(args.package))
    try:
        getattr(package, '__path__')
        generate_doc_for_package(package, args.output, args.no_header)
    except AttributeError:
        generate_doc_for_module(package, args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('package', help="A package/module to be documented")
    parser.add_argument('--output', help="A file to output",
                        type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('--no-header', help="Do not generate package header",
                        action='store_true')
    args = parser.parse_args()
    main(args)
