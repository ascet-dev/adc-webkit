#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup


def get_long_description():
    with open('README.md', encoding='utf8') as f:
        return f.read()


def get_packages(package):
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]


setup(
    name='adc-webkit',
    version='0.1.0',
    url='https://github.com/ascet-dev/adc-webkit',
    python_requires='>=3.8',
    install_requires=[
        'jose>=3.3.0',
        'pydantic>=2.0.0',
        'starlette>=0.27.0',
        'ujson>=5.8.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'docs': [
            'mkdocs>=1.4.0',
            'mkdocs-material>=9.0.0',
        ],
    },
    license='MIT',
    description='Toolkit for building web applications',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    packages=get_packages('adc_webkit'),
    include_package_data=True,
    data_files=[('', [])],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    zip_safe=False,
)
