# coding: utf-8

from __future__ import unicode_literals

import setuptools


with open("README.md", 'r') as f:
    long_description = f.read()


setuptools.setup(
    name="ezcache",
    version="1.0.0",
    author="Ilya Yurtaev",
    author_email="ilya.yurtaev@gmail.com",
    description="ezcache -- configurable cache decorator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ilya-yurtaev/ezcache",
    packages=setuptools.find_packages(),
    platforms='Platform independent',
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
