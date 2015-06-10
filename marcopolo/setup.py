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
import os, sys
import subprocess
import glob

def detect_init():
    try:
        subprocess.check_call(["systemctl", "--version"], stdout=None, stderr=None, shell=False)
        return 0
    except (subprocess.CalledProcessError, OSError):
        return 1

def enable_service(service):
    sys.stdout.write("Enabling service " + service +"...")
    if init_bin == 0:
        subprocess.call(["systemctl", "enable", service], shell=False)
    else:
        subprocess.call(["update-rc.d", service, "defaults"], shell=False)
    
    print("Enabled!")

if __name__ == "__main__":
    
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
        long_description = f.read()

    
    
    data_files = [
                 ('/etc/marcopolo/marco', ["etc/marcopolo/marco/marco.conf"]),
                 ('/etc/marcopolo/polo/', ["etc/marcopolo/polo/polo.conf"]),
                 ('/etc/marcopolo/polo/services', [os.path.join("etc/marcopolo/polo/services/", d) for d in os.listdir("etc/marcopolo/polo/services/")]),
                 ('/etc/marcopolo', ["etc/marcopolo/marcopolo.conf"]),
                 ]

    init_bin = detect_init()
    if init_bin == 1:
        daemon_files = [
                         ('/etc/init.d/', ["daemon/systemv/marco", "daemon/systemv/polo"])
                       ]

    else:
        daemon_files = [('/etc/systemd/system/', ["daemon/marco.service", "daemon/polo.service"]),
                         ('/usr/local/bin/', glob.glob("daemon/*.py"))
                       ]

    data_files.extend(daemon_files)

    setup(
        name='marcopolo',
        namespace_packages=['marcopolo'],
        provides=["marcopolo.marco", "marcopolo.polo"],
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

        #packages=['marcopolo.marco', 'marcopolo.polo', 'marcopolo.marco_conf'],
        packages=find_packages(),
        install_requires=[
            'Twisted==15.1.0'
        ],
        zip_safe=False,
        data_files=data_files,

        entry_points={
            'console_scripts': ['polo = marcopolo.polo.polod:main',
                                'marco = marcopolo.marco.marcod:main'],
        },
    )

    enable_service("marco")