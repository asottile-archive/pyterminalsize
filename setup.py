import os
import re
import sys

from setuptools import Extension
from setuptools import setup

if sys.platform == 'win32':
    versions = [
        var for var in os.environ
        if var.startswith('VS') and var.endswith('COMNTOOLS')
    ]
    vs = sorted(versions, key=lambda s: int(re.search('\d+', s).group()))[-1]
    os.environ['VS90COMNTOOLS'] = os.environ[vs]  # py2
    os.environ['VS100COMNTOOLS'] = os.environ[vs]  # py3

setup(
    name='pyterminalsize',
    description='Determines terminal size in a cross-platform way.',
    url='https://github.com/asottile/pyterminalsize',
    version='0.1.0',
    author='Anthony Sottile',
    author_email='asottile@umich.edu',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    py_modules=['pyterminalsize'],
    ext_modules=[Extension('_pyterminalsize', ['_pyterminalsize.c'])],
    install_requires=[],
)
