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

from yaql.language import utils


class YaqlInterface(object):
    def __init__(self, context, engine, receiver=utils.NO_VALUE):
        self.__sender = receiver
        self.__engine = engine
        self.__context = context

    @property
    def context(self):
        return self.__context

    @property
    def engine(self):
        return self.__engine

    @property
    def sender(self):
        return self.__sender

    def on(self, receiver):
        return YaqlInterface(self.context, self.engine, receiver)

    def __getattr__(self, item):
        def stub(*args, **kwargs):
            context = self.context
            args = utils.convert_input_data(args)
            kwargs = utils.convert_input_data(kwargs)
            limit_func = context('#iter', self.engine)
            return utils.convert_output_data(
                context(item, self.engine, self.sender)(*args, **kwargs),
                limit_func, self.engine)
        return stub

    def __call__(self, __expression, *args, **kwargs):
        context = self.context.create_child_context()
        args = utils.convert_input_data(args)
        for i, arg_value in enumerate(args):
            context['$' + str(i + 1)] = arg_value

        kwargs = utils.convert_input_data(kwargs)
        for arg_name, arg_value in kwargs.items():
            context['$' + arg_name] = arg_value

        parsed = self.engine(__expression)
        res = parsed.evaluate(context=context)
        limit_func = context('#iter', self.engine)
        return utils.convert_output_data(res, limit_func, self.engine)

    def __getitem__(self, item):
        return self.context[item]

    def __setitem__(self, key, value):
        self.context[key] = value
