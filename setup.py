#!/usr/bin/env python

import os
import re

from setuptools import setup, find_packages

version_file = os.path.join(
    os.path.dirname(__file__),
    'mass_api_client',
    '__version__.py'
)

with open(version_file, 'r') as fp:
    m = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        fp.read(),
        re.MULTILINE
    )
    version = m.groups(1)[0]

setup(name='mass_api_client',
      version=version,
      license='MIT',
      url='https://github.com/mass-project/mass_api_client',
      install_requires=['requests==2.18.1', 'marshmallow==2.13.5'],
      packages=find_packages(),
      )
