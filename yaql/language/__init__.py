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

import six


def _python_2_unicode_compatible(class_):
    """
    A decorator that defines __unicode__ and __str__ methods under Python 2.
    Under Python 3 it does nothing.

    To support Python 2 and 3 with a single code base, define a __str__ method
    returning text and apply this decorator to the class.

    Copyright (c) 2010-2015 Benjamin Peterson
    """
    if six.PY2:
        if '__str__' not in class_.__dict__:
            raise ValueError("@python_2_unicode_compatible cannot be applied "
                             "to %s because it doesn't define __str__()." %
                             class_.__name__)
        class_.__unicode__ = class_.__str__
        class_.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return class_

if not hasattr(six, 'python_2_unicode_compatible'):
    six.python_2_unicode_compatible = _python_2_unicode_compatible
