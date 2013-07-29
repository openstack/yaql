import ns.definition


class Customer():
    def __init__(self, _id, email):
        self.id = _id
        self.email = email


users = [Customer(1, 'user1@yandex.ru'),
         Customer(2, 'user2@yandex.ru'),
         Customer(3, 'user3@yandex.ru')]

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


data = {'users': users, 'services': services}

ns.definition.register_shortening('yaql', 'com.mirantis.murano.yaql')
ns.definition.register_shortening('ex', 'com.mirantis.murano.examples')
ns.definition.register_symbol('com.mirantis.murano.yaql', 'version')
ns.definition.register_symbol('com.mirantis.murano.yaql', 'name')
ns.definition.register_symbol('com.mirantis.murano.yaql', 'position')
ns.definition.register_symbol('com.mirantis.murano.yaql', 'description')
ns.definition.register_symbol('com.mirantis.murano.yaql', 'owner')
ns.definition.register_symbol('com.mirantis.murano.yaql', 'parent_service')
ns.definition.register_symbol('com.mirantis.murano.examples', 'Service0')
ns.definition.register_symbol('com.mirantis.murano.examples', 'Service1')
