Bindings
========

Applications on a node can get access to the Marco and Polo data through a series of functions available on a set of bindings and shell commands. The main functionality of those bindings is dedicated to the discovery of nodes. Nonetheless, some other information is also made available.

There are three bindings for three different languages: C (and of course C++), Python and Java, offering the same functionality in the same fashion, yet taking advantage of the particular features of each languaje.

The bindings are inspired by the netdb.h functions used in order to resolve host and DNS names, and as such they communicate with the local Marco or Polo instance through local sockets (on 127.0.1.1 port 1337 and 1338).

For the sake of consistency with the usual Marco Polo commands, all data is encoded in UTF-8 JSON strings with a similar structure.

All bindings implement this set of functions:

Python binding

Marco functions

.. py:function:: request_for(service, timeout=None)
	
	Returns a :py:func:`set` of nodes offering the requested *service*.
	Please note that the function will block the execution of the thread until the timeout in the Marco configuration file is triggered. Though this should not be a problem for most application, it is worth knowing.
	If *timeout* is set to an integer, the resolver will override its local *timeout* parameter and use this instead for the resolving process.
	It throws a MarcoTimeOutException in the event that no connection can be made to the local resolver (probably due a failure start of the daemon).

.. py:function:: getOneNode(criteria=None, timeout=None)

	Returns one node picked at random from the responses (more precisely, the first replying node) or the one which best satisfies the given criteria.

.. py:function:: getAllNodes(timeout=None)

	Gets all nodes available on the net, without regard of the offered services.
	It throws a MarcoTimeOutException in the event that no connection can be made to the local resolver (probably due a failure start of the daemon).

.. py:function:: getNodeInfo(ip)

	Gets the information of a node if it is available on the network.

Polo functions

.. py:function:: register_service(service, params=None)

	Adds a new service to the set of offered ones. The service will only be offered through the life cycle of the calling node, and will be deregistered upon the end of it.
	In order to make a service permanently available please refer to the :doc:`/services` documentation.

.. py:function:: remove_service(service)

	Removes a service from the offered ones. Please note that it is required to have the `ownership` of the service (that is, the only process which can remove a service is the process which created it or the Polo instance itself) for the function to be successful. Otherwise, a PoloPermissionDeniedException will be triggered.

.. py:function:: have_service(service)

	Returns True if the *service* is offered. Otherwise it returns *False*
