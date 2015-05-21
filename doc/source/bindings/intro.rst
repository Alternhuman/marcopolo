Bindings
========

Applications on a node can get access to the Marco and Polo functionality through a series of functions available on a set of bindings and shell commands. The main functionality of those bindings is dedicated to the discovery of nodes. Nonetheless, some other information has also been made available.

There are three bindings for three different languages: C++ (C compatible), Python and Java, offering the same functionality in the same fashion, yet taking advantage of the particular features of each languaje.

The bindings are inspired by the netdb.h functions used in order to resolve host and DNS names, and as such they communicate with the local Marco or Polo instance through local sockets (on 127.0.1.1 port 1337 and 1338).

For the sake of consistency with the usual Marco Polo commands, all data is encoded in UTF-8 JSON strings with a similar structure.

All bindings implement this set of functions:

Python binding

Marco functions

.. autoclass:: bindings.marco.marco.Marco
	:members:

.. py:function:: service_params(node, max_nodes=None, params=Node, timeout=None)

	C struct node * service_params(char * node, struct service params, int timeout)
	C++ std::vector<node> service_params(char * node, service params, int timeout)
	Java ArrayList<Node> service_params(string node, service node, int timeout)

	Returns all the nodes in the net which satisfy the given params for a certain service.

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

.. autoclass:: bindings.polo.polo.Polo
	:members:


..automethod: bindings.polo.polo.Polo.publish_service
