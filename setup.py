#!/usr/bin/env python
from setuptools import setup

setup(name='sendtx',
      version='0.5',
      description='Send serialized bitcoin transaction from commandline to bitcoin network',
      author='slush',
      author_email='info@bitcion.cz',
      url='https://github.com/slush0/sendtx',
      license='public domain',
      packages=['sendtx',],
      install_requires=['twisted',],
      scripts=['scripts/sendtx',],
      zip_safe=True,
     )
