Marco methods
-------------

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