#!/usr/bin/env python
# coding=utf-8

from distutils.core import setup
import os

setup(
    name="foamPy",
    version="0.0.1",
    author="Pete Bachant",
    author_email="petebachant@gmail.com",
    packages=["foampy"],
    scripts=["scripts/foampy-progress-bar"],
    url="https://github.com/petebachant/foamPy.git",
    license="MIT",
    description="Python package for working with OpenFOAM.",
    long_description=open("README.md").read(),
    install_requires=["numpy"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Topic :: Scientific/Engineering :: Physics"],
)
