#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io

from setuptools import setup


def read_file(filename):
    with io.open(filename, encoding='UTF-8') as fp:
        return fp.read().strip()


def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


packages = ['fish_core', 'fish_crawlers', 'fish_dashboard', 'fish_searcher']

setup(
    name='FishFishJump',
    version=read_file('VERSION'),
    description='FishFishJump is a solution that simply and basic for search engines and provide multiple demos that independent deployment by used Docker.',
    long_description=read_file('README.rst'),
    author='SylvanasSun',
    author_email='sylvanas.sun@gmail.com',
    url='https://github.com/SylvanasSun/FishFishJump',
    packages=packages,
    install_requires=read_requirements('requirements.txt'),
    include_package_data=True,
    license='MIT',
    keywords='FishFishJump python scrapy scrapy-redis search engines',
    entry_points={
        'console_scripts': [
            'fish_dashboard=fish_dashboard.app:main',
            'fish_searcher=fish_searcher.app:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
