#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The MarcoPolo bindings
"""

from setuptools import setup, find_packages

from codecs import open
from os import path
from distutils.core import setup
from distutils.command.clean import clean
from distutils.command.install import install
import os

here = path.abspath(path.dirname(__file__))

if __name__ == "__main__":
    

    with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
        long_description = f.read()

    setup(
        name='marcopolobindings',
        #cmdclass={'install': MyInstall},
        namespace_packages=['marcopolo'],
        provides=["marcopolo.bindings"],
        version='0.0.1',

        description='A python binding for MarcoPolo',

        long_description=long_description,

        url='',

        author='Diego Martín',

        author_email='martinarroyo@usal.es',

        license='MIT',

        classifiers=[
            'Development Status :: 3 - Alpha',

            'Intended Audience :: Developers',

            'Topic :: Software Development :: Build Tools',

            'License :: OSI Approved :: MIT License',

            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',

        ],

        keywords="marcopolo discovery binding",

        #packages=['marcopolo.bindings.marco', 'marcopolo.bindings.polo', 'marcopolo.bindings.marco_conf'],
        packages=find_packages(),
        #install_requires=[''],
        #package_data={
        #    'sample': ['package_data.dat'],
        #},
        #data_files=[('my_data', ['data/data_file'])],

        # entry_points={
        #     'console_scripts': [
        #         'marcopolobindings=marcopolobindings:main',
        #     ],
        # },
    ) 