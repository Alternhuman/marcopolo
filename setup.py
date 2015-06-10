#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The MarcoPolo reference implementation
"""

from setuptools import setup, find_packages

from codecs import open
from os import path
from distutils.core import setup
from distutils.command.clean import clean
from distutils.command.install import install
import os



class MyInstall(install):
    #http://stackoverflow.com/a/30241551/2628463
    # Calls the default run command, then deletes the build area
    # (equivalent to "setup clean --all").
    def run(self):
        install.run(self)
        # c = clean(self.distribution)
        # c.all = True
        # c.finalize_options()
        # c.run()

if __name__ == "__main__":
    
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
        long_description = f.read()

    
    
    data_files = ([('/etc/marcopolo/marco', ["etc/marcopolo/marco/marco.conf"]),
                 ('/etc/marcopolo/polo', ["etc/marcopolo/polo/polo.conf"]
                                         + [os.path.join("etc/marcopolo/polo/services/", d) for d in os.listdir("etc/marcopolo/polo/services/")]),
                 ('/etc/marcopolo', ["etc/marcopolo/marcopolo.conf"]),
                 ('/etc/init.d/', ["daemon/systemv/marco",
                                  "daemon/systemv/polo"])
                 ])

    setup(
        name='marcopolo',
        cmdclass={'install': MyInstall},
        version='0.0.1',

        description='The reference implementation for MarcoPolo',

        long_description=long_description,

        url='marcopolo.martinarroyo.net',

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

        packages=['marcopolo.marco', 'marcopolo.polo', 'marcopolo.marco_conf'],

        install_requires=[
            'Twisted==15.1.0',
            'zope.interface==4.1.2'
        ],

        data_files=data_files,

        entry_points={
            'console_scripts': [
                'marcopolobindings=marcopolobindings:main',
            ],
        },
    ) 