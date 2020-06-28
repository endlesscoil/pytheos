#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='pytheos',
    version='0.1.0',
    description='HEOS Library for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/endlesscoil/pytheos',
    author='Scott Petersen',
    author_email='scott@digression.org',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='python heos marantz denon network audio api',
    #package_dir={'pytheos': '.'},
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'netifaces',
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    # package_data={},
    # entry_points={
    #     'console_scripts': [
    #         'pytheos=pytheos:main',
    #     ],
    # },
    project_urls={
        'Source': 'https://github.com/endlesscoil/pytheos',
    },
)
