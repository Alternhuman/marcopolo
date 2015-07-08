#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The MarcoPolo reference implementation
"""

from setuptools import setup, find_packages

from codecs import open
import os
from distutils.core import setup
from distutils.command.clean import clean
from distutils.command.install import install
import os, sys
import subprocess
import glob
import stat

custom_marcopolo_params = [
                            "--marcopolo-disable-daemons",
                            "--marcopolo-disable-marco", 
                            "--marcopolo-enable-polo",
                            "--marcopolo-no-start"
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
    
    sys.stdout.write("Enabled!")

def start_service(service):
    sys.stdout.write("Starting service " + service + "...")
    if init_bin == 0:
        subprocess.call(["systemctl", "start", service], shell=False)
    else:
        subprocess.call(["service", service, "start"], shell=False)

    sys.stdout.write("Started!")

def set_cert_permissions():
    for cert in os.listdir("/etc/marcopolo/certs"):
        os.chmod(os.path.join("/etc/marcopolo/certs", cert), stat.S_IREAD | stat.S_IWRITE)

    os.chmod("/etc/marcopolo/certs", stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

    os.chmod('/etc/marcopolo/polo/secret', stat.S_IREAD | stat.S_IWRITE )

if __name__ == "__main__":
    marcopolo_params = []

    python_version = int(sys.version[0])

    for param in sys.argv:
        if param in custom_marcopolo_params:
            marcopolo_params.append(param)
            sys.argv.remove(param)


    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
        long_description = f.read()



    data_files = [
                 ('/etc/marcopolo/marco', glob.glob("etc/marcopolo/marco/*.*")),
                 ('/etc/marcopolo/polo/', glob.glob("etc/marcopolo/polo/*.*")),
                 ('/etc/marcopolo/polo/', ["etc/marcopolo/polo/secret"]),
                 ('/etc/marcopolo/polo/services', [os.path.join("etc/marcopolo/polo/services/", d) for d in os.listdir("etc/marcopolo/polo/services/")]),
                 ('/etc/marcopolo/certs', [os.path.join("etc/marcopolo/certs", f) for f in os.listdir("etc/marcopolo/certs/")]),
                 ]

    if "--marcopolo-disable-daemons" not in marcopolo_params:
        init_bin = detect_init()
        if python_version == 2:
            if init_bin == 1:
                daemon_files = [
                                 ('/etc/init.d/', ["daemon/systemv/marcod", "daemon/systemv/polod"])
                               ]

            else:
                daemon_files = [('/etc/systemd/system/', ["daemon/marcod.service", "daemon/polod.service"]),
                                 ('/usr/local/bin/', glob.glob("daemon/*.py"))
                               ]
            
            data_files.extend(daemon_files)

            twistd_files = [('/etc/marcopolo/daemon', ["daemon/twistd/marco_twistd.tac", 
                                                       "daemon/twistd/polo_twistd.tac"])
                           ]
            data_files.extend(twistd_files)

        elif python_version == 3:
            if init_bin == 1:
                daemon_files = [
                                 ('/etc/init.d/', ["daemon/python3/systemv/marcod", "daemon/python3/systemv/polod"])
                               ]

            else:
                daemon_files = [('/etc/systemd/system/', ["daemon/python3/marcod.service", "daemon/python3/polod.service"]),
                                 ('/usr/local/bin/', glob.glob("daemon/python3/*.py"))
                               ]
            
            data_files.extend(daemon_files)
    version = '0.1.7'
    setup(
        name='marcopolo',
        namespace_packages=['marcopolo'],
        provides=["marcopolo.marco", "marcopolo.polo"],
        version=version,

        description='The reference implementation for MarcoPolo',

        long_description=long_description,

        url='marcopolo.martinarroyo.net',
        download_url='https://bitbucket.org/Alternhuman/marcopolo/get/v'+version+'.tar.gz',

        author='Diego Martín',

        author_email='martinarroyo@usal.es',

        license='MIT',

        classifiers=[
            'Development Status :: 3 - Alpha',

            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',

            'Topic :: Software Development :: Build Tools',
            'Topic :: System :: Networking',
            'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',

            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Natural Language :: English',
        ],

        keywords="marcopolo discovery binding",

        packages=find_packages(),
        install_requires=[
            'Twisted>=15.1.0',
            'pyOpenSSL>=0.15.1',
            'service_identity>=14.0.0',
            'six>=1.9.0',
            'pycrypto>=2.6.1'
        ],
        zip_safe=False,
        data_files=data_files,

        entry_points={
            'console_scripts': ['polod = marcopolo.polo.polod:main',
                                'marcod = marcopolo.marco.marcod:main'],
        },
    )

    if "install" in sys.argv:

        if "--marcopolo-disable-daemons" not in marcopolo_params:
            if "--marcopolo-disable-marco" not in marcopolo_params:
                enable_service("marcod")
                if "--marcopolo-no-start" not in marcopolo_params:
                    start_service("marcod")

            if "--marcopolo-enable-polo" in marcopolo_params:
                enable_service("polod")
                if "--marcopolo-no-start" not in marcopolo_params:
                    start_service("polod")

        if not os.path.exists("/var/log/marcopolo"):
            os.makedirs('/var/log/marcopolo')

        set_cert_permissions()
