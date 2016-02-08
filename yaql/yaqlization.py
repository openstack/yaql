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

import six


YAQLIZATION_ATTR = '__yaqlization__'


def yaqlize(class_or_object=None, yaqlize_attributes=True,
            yaqlize_methods=True, yaqlize_indexer=True,
            auto_yaqlize_result=False, whitelist=None, blacklist=None,
            attribute_remapping=None, blacklist_remapped_attributes=True):
    def func(something):
        if not hasattr(something, YAQLIZATION_ATTR):
            setattr(something, YAQLIZATION_ATTR, build_yaqlization_settings(
                yaqlize_attributes=yaqlize_attributes,
                yaqlize_methods=yaqlize_methods,
                yaqlize_indexer=yaqlize_indexer,
                auto_yaqlize_result=auto_yaqlize_result,
                whitelist=whitelist,
                blacklist=blacklist,
                attribute_remapping=attribute_remapping,
            ))
        return something
    if class_or_object is None:
        return func
    else:
        return func(class_or_object)


def get_yaqlization_settings(class_or_object):
    return getattr(class_or_object, YAQLIZATION_ATTR, None)


def is_yaqlized(class_or_object):
    return hasattr(class_or_object, YAQLIZATION_ATTR)


def build_yaqlization_settings(
        yaqlize_attributes=True, yaqlize_methods=True, yaqlize_indexer=True,
        auto_yaqlize_result=False, whitelist=None, blacklist=None,
        attribute_remapping=None, blacklist_remapped_attributes=True):
    whitelist = set(whitelist or [])
    blacklist = set(blacklist or [])
    attribute_remapping = attribute_remapping or {}
    if blacklist_remapped_attributes:
        for value in six.itervalues(attribute_remapping):
            if not isinstance(value, six.string_types):
                name = value[0]
            else:
                name = value
            blacklist.add(name)

    return {
        'yaqlizeAttributes': yaqlize_attributes,
        'yaqlizeMethods': yaqlize_methods,
        'yaqlizeIndexer': yaqlize_indexer,
        'autoYaqlizeResult': auto_yaqlize_result,
        'whitelist': whitelist,
        'blacklist': blacklist,
        'attributeRemapping': attribute_remapping
    }
