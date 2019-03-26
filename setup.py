#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'hseling-api-direct-speech'
DESCRIPTION = 'HSE Linguistics API: Direct Speech'
URL = 'https://github.com/hseling/hseling-api-direct-speech'
EMAIL = 'ssobko@hse.ru'
AUTHOR = 'Sergey Sobko'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '1.0.0'

REQUIRED = ["flask", "redis", "celery[redis]", "minio", "requests", "lxml", "html5lib", "beautifulsoup4", "pymorphy2", "nltk"]

EXTRAS = {}

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests', 'app', 'nltk_data')),
    package_data={
      'hseling_api_direct_speech': ['csv_files/*.csv'],
   },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    cmdclass={},
)
