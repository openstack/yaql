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

from setuptools import setup, find_packages

setup(name='yaql',
      version='0.2.1',
      description="Yet Another Query Language",
      author='Mirantis, Inc.',
      author_email='info@mirantis.com',
      url='http://mirantis.com',
      install_requires=['ply'],
      entry_points={
          'console_scripts': [
              'yaql=yaql.cli.run:main',
          ]
      },
      packages=find_packages(),
      package_data={
          'examples': ['*.json'],
      },)
