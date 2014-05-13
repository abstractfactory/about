# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup, find_packages

path = os.path.dirname(__file__)
sys.path.insert(0, path)

import about
version = about.version

f = open('README.md')
readme = f.read().strip()

f = open('LICENSE.md')
license = f.read().strip()

setup(
    name='about',
    version=version,
    description='About',
    long_description=readme,
    author='Abstract Factory Ltd.',
    author_email='marcus@abstractfactory.com',
    url='https://github.com/abstractfactory/about',
    license=license,
    packages=find_packages(),
    package_data={
        'about': ['*.pyw',
                  '*.css',
                  'bin/*.py'
                  'bin/*.pyw'],
    },
    include_package_data=True,
)
