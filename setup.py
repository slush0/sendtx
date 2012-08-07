#!/usr/bin/env python
#from distribute_setup import use_setuptools
#use_setuptools()

from distutils.core import setup

setup(name='sendtx',
      version='0.5',
      description='Send serialized bitcoin transaction from commandline to bitcoin network',
      author='slush',
      author_email='info@bitcion.cz',
      url='https://github.com/slush0/sendtx',
      license='public domain',
      packages=['sendtx',],
      requires=['twisted',],
      scripts=['scripts/sendtx',],
     )
