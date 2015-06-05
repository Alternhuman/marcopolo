Polo functions
--------------

.. py:function:: register_service(service, params=None)

	Adds a new service to the set of offered ones. The service will only be offered through the life cycle of the calling node, and will be deregistered upon the end of it.
	In order to make a service permanently available please refer to the :doc:`/services` documentation.

.. py:function:: remove_service(service)

	Removes a service from the offered ones. Please note that it is required to have the `ownership` of the service (that is, the only process which can remove a service is the process which created it or the Polo instance itself) for the function to be successful. Otherwise, a PoloPermissionDeniedException will be triggered.

.. py:function:: have_service(service)

	Returns True if the *service* is offered. Otherwise it returns *False*

.. autoclass:: bindings.polo.polo.Polo
	:members: