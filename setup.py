#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io

from setuptools import setup


def read_file(filename):
    with io.open(filename) as fp:
        return fp.read().strip()


def read_rst(filename):
    # Ignore unsupported directives by pypi.
    content = read_file(filename)
    return ''.join(line for line in io.StringIO(content)
                   if not line.startswith('.. comment::'))


def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


packages = ['fish_core', 'fish_crawlers', 'fish_dashboard']

setup(
    name='FishFishJump',
    version=read_file('VERSION'),
    description='Simple solution for search engines in the python',
    long_description=read_rst('README.rst') + '\n\n' + read_rst('HISTORY.rst'),
    author='SylvanasSun',
    author_email='sylvanas.sun@gmail.com',
    url='https://github.com/SylvanasSun/FishFishJump',
    packages=packages,
    install_requires=read_requirements('requirements.txt'),
    include_package_data=True,
    license='MIT',
    keywords='FishFishJump python scrapy scrapy-redis',
    entry_points={
        'console_scripts': [
            'fish_dashboard=fish_dashboard.app:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
