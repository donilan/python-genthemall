#!/usr/bin/env python

import sys, multiprocessing

from setuptools import setup, find_packages

from genthemall.version import get_version

setup (
    name = 'GenThemAll',
    version = get_version('short'),
    description = 'GenThemAll is a simple, Pythonic tool for genernate code and whatevery you want.',
    author = 'Doni',
    author_email = 'd@ii2d.com',
    packages = find_packages(),
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    install_requires = ['config'],
    entry_points = {
        'console_scripts': [
            'genthemall = genthemall.main:main',
            ]
        },
    classifiers = [
    ],
)
