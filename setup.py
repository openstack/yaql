from setuptools import setup, find_packages

setup(name='yaql',
      version='0.1',
      description="Yet Another Query Language",
      author='Mirantis, Inc.',
      author_email='info@mirantis.com',
      url='http://mirantis.com',
      install_requires=['ply'],
      packages=find_packages())
