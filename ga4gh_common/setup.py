"""
Assists with packages' setup.py
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


readmeFilename = "README.pypi.rst"
requirementsFilename = "requirements.txt"
defaultDict = {
    "license": 'Apache License 2.0',
    "include_package_data": True,
    "zip_safe": True,
    "author": "Global Alliance for Genomics and Health",
    "author_email": "theglobalalliance@genomicsandhealth.org",
    "entry_points": {},
    "classifiers": [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    "keywords": 'genomics reference',
    # Use setuptools_scm to set the version number automatically from Git
    "setup_requires": ['setuptools_scm'],
}


def _doImports():
    # First, we try to use setuptools. If it's not available locally,
    # we fall back on ez_setup.
    try:
        from setuptools import setup
    except ImportError:
        from ez_setup import use_setuptools
        use_setuptools()
        from setuptools import setup
    return setup


def _getLongDescription():
    with open(readmeFilename) as readmeFile:
        long_description = readmeFile.read()
    return long_description


def _getInstallRequires():
    install_requires = []
    with open(requirementsFilename) as requirementsFile:
        for line in requirementsFile:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            pinnedVersion = line.split()[0]
            install_requires.append(pinnedVersion)


def _getSetupDict(packageDict):
    long_description = _getLongDescription()
    install_requires = _getInstallRequires()
    attrDict = {
        "long_description": long_description,
        "install_requires": install_requires,
    }
    setupDict = {}
    setupDict.update(defaultDict)
    setupDict.update(attrDict)
    setupDict.update(packageDict)
    return setupDict


def doSetup(packageDict):
    setup = _doImports()
    setupDict = _getSetupDict(packageDict)
    setup(**setupDict)
