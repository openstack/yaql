# Copyright (c) 2016 Mirantis, Inc.
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

import importlib
import io
import operator
import pkgutil
import traceback
import types

from docutils import nodes
from docutils.parsers import rst
from docutils import utils


TAG = ':yaql:'


def _get_modules_names(package):
    """Get names of modules in package"""

    return sorted(
        map(operator.itemgetter(1),
            pkgutil.walk_packages(package.__path__,
                                  '{0}.'.format(package.__name__))))


def _get_functions_names(module):
    """Get names of the functions in the current module"""

    return [name for name in dir(module) if
            isinstance(getattr(module, name, None), types.FunctionType)]


def write_method_doc(method, output):
    """Construct method documentation from a docstring.

    1) Strip TAG
    2) Embolden function name
    3) Add :callAs: after :signature:
    """

    msg = "Error: function {0} has no valid YAQL documentation."

    if method.__doc__:
        doc = method.__doc__
        try:
            # strip TAG
            doc = doc[doc.index(TAG) + len(TAG):]

            # embolden function name
            line_break = doc.index('\n')
            yaql_name = doc[:line_break]
            (emit_header, is_overload) = yield yaql_name
            if emit_header:
                output.write(yaql_name)
                output.write('\n')
                output.write('~' * len(yaql_name))
                output.write('\n')
            doc = doc[line_break:]

            # add :callAs: parameter
            try:
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
                text = doc[:position] + call_as_str + doc[position:]
            except ValueError:
                text = doc
            if is_overload:
                text = '*  ' + '\n   '.join(text.split('\n'))
                output.write(text)
            else:
                output.write(text)
        except ValueError:
            yield method.func_name
            output.write(msg.format(method.func_name))


def write_module_doc(module, output):
    """Generate and write rst document for module.

    Generate and write rst document for the single module.

    :parameter module: takes a Python module which should be documented.
    :type module: Python module

    :parameter output: takes file to which generated document will be written.
    :type output: file
    """
    functions_names = _get_functions_names(module)
    if module.__doc__:
        output.write(module.__doc__)
        output.write('\n')
    seq = []
    for name in functions_names:
        method = getattr(module, name)
        it = write_method_doc(method, output)
        try:
            name = next(it)
            seq.append((name, it))
        except StopIteration:
            pass
    seq.sort(key=operator.itemgetter(0))
    prev_name = None
    for i, item in enumerate(seq):
        name = item[0]
        emit_header = name != prev_name
        prev_name = name
        if emit_header:
            overload = i < len(seq) - 1 and seq[i + 1][0] == name
        else:
            overload = True

        try:
            item[1].send((emit_header, overload))
        except StopIteration:
            pass
        output.write('\n\n')
    output.write('\n')


def write_package_doc(package, output):
    """Writes rst document for the package.

    Generate and write rst document for the modules in the given package.

    :parameter package: takes a Python package which should be documented
    :type package: Python module

    :parameter output: takes file to which generated document will be written.
    :type output: file
    """

    modules = _get_modules_names(package)
    for module_name in modules:
        module = importlib.import_module(module_name)
        write_module_doc(module, output)


def generate_doc(source):
    try:
        package = importlib.import_module(source)
    except ImportError:
        return 'Error: No such module {0}'.format(source)
    out = io.StringIO()
    try:
        if hasattr(package, '__path__'):
            write_package_doc(package, out)
        else:
            write_module_doc(package, out)
        res = out.getvalue()
        return res

    except Exception as e:
        return '.. code-block:: python\n\n    Error: {0}\n    {1}\n\n'.format(
            str(e), '\n    '.join([''] + traceback.format_exc().split('\n')))


class YaqlDocNode(nodes.General, nodes.Element):
    source = None

    def __init__(self, source):
        self.source = source
        super(YaqlDocNode, self).__init__()


class YaqlDocDirective(rst.Directive):
    has_content = False
    required_arguments = 1

    def run(self):
        return [YaqlDocNode(self.arguments[0])]


def render(app, doctree, fromdocname):
    for node in doctree.traverse(YaqlDocNode):
        new_doc = utils.new_document('YAQL', doctree.settings)
        content = generate_doc(node.source)
        rst.Parser().parse(content, new_doc)
        node.replace_self(new_doc.children)


def setup(app):
    app.add_node(YaqlDocNode)
    app.add_directive('yaqldoc', YaqlDocDirective)
    app.connect('doctree-resolved', render)
    return {'version': '0.1'}
