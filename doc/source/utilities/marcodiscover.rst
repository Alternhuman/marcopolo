Marcodiscover
-------------

MarcoDiscover is a Python script that communicates with the Marco instance on the machine. It translates the user input to a MarcoPolo command and formats the response in several different styles.

MarcoDiscover is able to execute every MarcoPolo command using arguments from the command line. For instance

::

	> marcodiscover 

Will return all the nodes in the network, sending the command marco.

::

	> marcodiscover -d <address>

Changes the multicast group where to look for nodes.

::

	> marcodiscover -s <service_id>

Will return all the nodes that offer the service identified by `service_id`.

::

	> marcodiscover -n <node>

Will return all the services in a node

::

	> marcodiscover -sh

Prints the output so it can be used as an iterable list in bash

::

	> marcodiscover --mpi-format

Prints the output so it can be used as a `hostfile` file in MPI.

