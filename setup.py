#!/usr/bin/env python
# coding=utf-8

from distutils.core import setup
import os

setup(
    name='foamPy',
    version='0.0.1',
    author='Pete Bachant',
    author_email='petebachant@gmail.com',
    packages=['foampy'],
    scripts=['scripts/foampy-progress-bar'],
    url='https://github.com/petebachant/foamPy.git',
    license='LICENSE',
    description='Python package for working with OpenFOAM.',
    long_description=open('README.md').read()
)
