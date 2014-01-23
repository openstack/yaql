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


def process_customer(customer):
    return customer.email


class Customer():
    def __init__(self, _id, email):
        self.id = _id
        self.email = email
        self.list_prop = [1, 2, 3, 4]

ns = {'com.examples.test.Symbol': 'Some Test NS-based data'}


users = [Customer(1, 'user1@example.com'),
         Customer(2, 'user2@example.com'),
         Customer(3, 'user3@example.com')]

services = [
    {
        'com.mirantis.murano.yaql.name': 'Service1',
        'com.mirantis.murano.yaql.version': '1.5.3.1237',
        'com.mirantis.murano.yaql.position': 1,
        'com.mirantis.murano.yaql.description': 'Some Windows service',
        'com.mirantis.murano.yaql.owner': 1,
        'com.mirantis.murano.yaql.parent_service': 'com.mirantis.murano.'
                                                   'examples.Service0'
    },
    {
        'com.mirantis.murano.yaql.name': 'Service2',
        'com.mirantis.murano.yaql.version': '2.1',
        'com.mirantis.murano.yaql.position': 2,
        'com.mirantis.murano.yaql.description': 'Another Windows service',
        'com.mirantis.murano.yaql.owner': 1,
        'com.mirantis.murano.yaql.parent_service': None
    },
    {
        'com.mirantis.murano.yaql.name': 'Service3',
        'com.mirantis.murano.yaql.version': None,
        'com.mirantis.murano.yaql.position': 3,
        'com.mirantis.murano.yaql.description': 'Some Linux service',
        'com.mirantis.murano.yaql.owner': 2,
        'com.mirantis.murano.yaql.parent_service': None
    },
    {
        'com.mirantis.murano.yaql.name': 'Service4',
        'com.mirantis.murano.yaql.version': '1.0',
        'com.mirantis.murano.yaql.position': 4,
        'com.mirantis.murano.yaql.description': 'Some MacOS service',
        'com.mirantis.murano.yaql.owner': 3,
        'com.mirantis.murano.yaql.parent_service': 'com.mirantis.murano.'
                                                   'examples.Service0'
    },
]


data = {'users': users, 'services': services, 'ns': ns}
