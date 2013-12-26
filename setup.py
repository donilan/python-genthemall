#!/usr/bin/env python

import sys, os

from setuptools import setup, find_packages

from genthemall.core import get_version

# Find template files and package them
data_files = []
for dirpath, dirnames, filenames in os.walk('genthemall'):
    files = []
    for f in filenames:
        if f.endswith('.gt'):
            files.append(os.path.join(dirpath, f))
    if files:
        data_files.append((dirpath, files))


setup (
    name = 'GenThemAll',
    version = get_version(),
    description = 'GenThemAll is a simple, Pythonic tool for genernate code and whatevery you want.',
    author = 'Doni',
    author_email = 'd@ii2d.com',
    url = 'https://github.com/donilan/python-genthemall',
    license = 'Apache License, Version 2.0',
    packages = find_packages(),
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    install_requires = ['config', 'mako'],
    entry_points = {
        'console_scripts': [
            'genthemall = genthemall.main:main',
        ]
    },
    data_files = data_files,
    classifiers = [
        'Environment :: Console',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License'
    ],
)
