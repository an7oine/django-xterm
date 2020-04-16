# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
  setup_requires='git-versiointi',
  name='django-xterm',
  description='Django-pohjainen Xterm.JS-pääteyhteys',
  url='https://github.com/an7oine/django-xterm.git',
  author='Antti Hautaniemi',
  author_email='antti.hautaniemi@me.com',
  licence='MIT',
  packages=find_packages(),
  include_package_data=True,
  install_requires=[
    'django-pistoke',
  ],
  entry_points={
    'django.sovellus': ['xterm = xterm'],
  },
  zip_safe=False,
)
