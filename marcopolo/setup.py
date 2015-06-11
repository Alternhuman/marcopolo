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

custom_marcopolo_params = [
                            "--marcopolo-disable-daemons",
                            "--marcopolo-disable-polo", 
                            "--marcopolo-enable-polo"
                          ]

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
        subprocess.call(["update-rc.d", "-f", service, "remove"], shell=False)
        subprocess.call(["update-rc.d", service, "defaults"], shell=False)
    
    print("Enabled!")

if __name__ == "__main__":
    
    marcopolo_params = []

    for param in sys.argv:
        if param in custom_marcopolo_params:
            marcopolo_params.append(param)
            sys.argv.remove(param)


    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
        long_description = f.read()

    
    
    data_files = [
                 ('/etc/marcopolo/marco', ["etc/marcopolo/marco/marco.conf"]),
                 ('/etc/marcopolo/polo/', ["etc/marcopolo/polo/polo.conf"]),
                 ('/etc/marcopolo/polo/services', [os.path.join("etc/marcopolo/polo/services/", d) for d in os.listdir("etc/marcopolo/polo/services/")]),
                 ('/etc/marcopolo', ["etc/marcopolo/marcopolo.conf"]),
                 ]

    if "--marcopolo-disable-daemons" not in marcopolo_params:
        init_bin = detect_init()
        if init_bin == 1:
            daemon_files = [
                             ('/etc/init.d/', ["daemon/systemv/marcod", "daemon/systemv/polod"])
                           ]

        else:
            daemon_files = [('/etc/systemd/system/', ["daemon/marco.service", "daemon/polo.service"]),
                             ('/usr/local/bin/', glob.glob("daemon/*.py"))
                           ]
        
        data_files.extend(daemon_files)

    twistd_files = [('/etc/marcopolo/daemon', ["daemon/twistd/marco_twistd.tac", 
                                               "daemon/twistd/polo_twistd.tac"])
                   ]

    data_files.extend(twistd_files)

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

        packages=find_packages(),
        install_requires=[
            'Twisted==15.1.0'
        ],
        zip_safe=False,
        data_files=data_files,

        entry_points={
            'console_scripts': ['polod = marcopolo.polo.polod:main',
                                'marcod = marcopolo.marco.marcod:main'],
        },
    )

    if "--marcopolo-disable-daemons" not in marcopolo_params:
        if "--marcopolo-disable-polo" not in marcopolo_params:
            enable_service("marcod")

        if "--marcopolo-enable-polo" in marcopolo_params:
            enable_service("polod")