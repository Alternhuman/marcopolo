.. _configuration_files:

Configuration files
-------------------

The behaviour of MarcoPolo is defined almost in its entirety by the configuration files. All parameters are defined in a single folder (``/etc/marcopolo``, usually). The main files and folders are the following:

.. code::

	/etc/marcopolo/
	|── marco
	|   |── marco.conf
	|── marcopolo.conf
	|── polo
	    |── polo.conf
	    |── services
	        |── deployer
	        |── marcobootstrap
        	...

- The ``marcopolo.conf`` sets the common parameters: timeout for responses, log and run files, etc.

- The ``marco.conf`` and ``polo.conf`` files determine the particular behaviour of each of the daemons. The listening ports, multicast groups and several other parameters are defined here.

- The services folder stores the information about the static services provided by the machine. Each one is located in a file with no extension, and the information is encoded in JSON strings.
