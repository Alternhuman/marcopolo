Installation
============

MarcoPolo is distributed as a Python package that includes the Marco and Polo functionality. When installed, the package copies the MarcoPolo python classes to a proper location, sets several shell commands, creates the auxiliary files and configures the daemon manager of the operating system to include Marco and Polo.

The package can be downloaded from the releases page or be installed directly using `Pip <https://pip.pypa.io/en/stable/>`_.

Dependencies
------------

MarcoPolo only depends on the Twisted framework to work. ``setup.py`` will download it during the installation process, if not previously installed. It has been tested on Twisted version 15.1.

Python version
--------------

Twisted has been tested on Python 2.7 and Python 3.4. 

Instalation from source
-----------------------

Download the package and issue the following commands:

::
	
	> tar xf marcopolo-<version>.tar.gz
	> cd marcopolo-<version>
	> python setup.py install # Run as root if required

Installation from pip

::
	
	> pip install marcopolo # Run as root if required

By default, the installation creates the daemon files, and enables only the marco functionality. Polo must be configured by the user. However, the installation can be customized using the following options:

- ``--marcopolo-disable-daemons`` Does not configure the daemons (useful when marcopolo will always be launched manually).
- ``--marcopolo-disable-marco`` Creates the daemon file for marco, but does not enable it.
- ``--marcopolo-enable-polo`` Enables the polo service during installation.
- ``--marcopolo-no-start`` The enabled services are started during the installation unless this option is set.

Daemons
-------

MarcoPolo has been tested to work in System V and systemd-based distributions. ``setup.py`` will detect which one is present in the machine and configure MarcoPolo accordingly. Please see :doc:`/daemons/introduction` for more information about the daemons.

Python 2 and 3
~~~~~~~~~~~~~~

The Twisted framework is not yet ported entirely to Python 3 [1]_, lacking the ``twistd`` utility on this version of the language, which is used to "daemonize" MarcoPolo. Therefore, on Python 3 versions the daemons execute using the functionality provided by the system daemon manager.

Files
-----

Binaries
~~~~~~~~

After installation, the following binaries will be created:

- ``polod``: The polo daemon

- ``marcod``: The marco daemon

Directories and files
~~~~~~~~~~~~~~~~~~~~~

The following files are created:

- ``/etc/marcopolo`` directory:
	
	- ``marcopolo.conf``: General configuration options

	- ``daemon``: If installed using Python 2, the folder will contain the .tac files necessary for twistd to run.

	- ``marco/marco.conf``: Marco configuration parameters.

	- ``polo/polo.conf``: Polo configuration parameters.

	- ``polo/services/``: Service description files.

- ``/var/log/marcopolo`` directory:
	
	- ``marcod.log``: The marco log file

	- ``polod.log``: The polo log file

	If installed on a Python 2 system, twistd will also create log files for each daemon, named ``marcod-twistd.log`` and ``polod-twistd.log`` respectively.

.. [1] Plan/Python3 - Twisted - (Last checked 11th June 2015) https://twistedmatrix.com/trac/wiki/Plan/Python3