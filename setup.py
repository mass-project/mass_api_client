#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='mass_api_client',
      version=0.1,
      install_requires=['requests==2.14.2', 'marshmallow==2.13.5'],
      packages=find_packages(),
     )
