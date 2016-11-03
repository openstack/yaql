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

import os
import subprocess

from docutils import nodes
from docutils.parsers import rst
from docutils import utils


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
        content = run_documenter(node.source)
        rst.Parser().parse(content, new_doc)
        node.replace_self(new_doc.children)


def run_documenter(source):
    path = os.path.join(os.path.abspath('.'), 'yaql/contrib/documenter.py')
    proc = subprocess.Popen(['python', path, source, '--no-header'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    retcode = proc.poll()
    return stdout if not retcode else stderr


def setup(app):
    app.info('Loading the yaql documenter extension')
    app.add_node(YaqlDocNode)
    app.add_directive('yaqldoc', YaqlDocDirective)
    app.connect('doctree-resolved', render)
    return {'version': '0.1'}
