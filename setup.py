#!/usr/bin/env python

from distutils.core import setup

setup(name='mass_api_client',
      version=0.1,
      install_requires=['requests==2.13.0', 'marshmallow==2.13.3'],
      packages=['mass_api_client', ],
      )
