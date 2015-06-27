# -*- coding: utf-8 -*-

"""
MarcoPolo utilities
"""

from setuptools import setup, find_packages
import os, glob

if __name__ == "__main__":

    here = os.path.abspath(os.path.dirname(__file__))
    
    with open(os.path.join(here, 'DESCRIPTION.rst')) as f:
        long_description = f.read()


    data_files = [
                     ('/usr/local/bin', glob.glob("shellutils/*.sh"))
                 ]

    setup(
        name="marcoutils",
        namespace_packages=['marcopolo'],
        provides=['marcopolo.utils'],
        version="0.0.1",
        description="A set of useful utilities for MarcoPolo",

        long_description=long_description,

        url='marcopolo.martinarroyo.net',

        author='Diego Martín',

        author_email='martinarroyo@usal.es',

        license='MIT',
        include_package_data=True,
        classifiers=[
            'Development Status :: 3 - Alpha',

            'Intended Audience :: Developers',

            'Topic :: Software Development :: Build Tools',
            'Operating System :: POSIX :: Linux',
            'License :: OSI Approved :: MIT License',

            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',

        ],

        keywords="marcopolo utilities",
        
        install_requires=["marcopolo>=0.0.1", "marcopolobindings>=0.0.1"],
        
        zip_safe=False,
        
        data_files=data_files,
        #packages=['marcopolo.utils'],
        packages=find_packages(),
        entry_points={
            'console_scripts': ['marcodiscover = marcopolo.utils.marcodiscover:main',
                                'marcoinstallkey = marcopolo.utils.marcoinstallkey:main'
                                ],
        },

    )