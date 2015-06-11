Definition of Services
======================

A *service* is a set of information that can be discovered by using a unique identifier (the service *name*). There are two types of services, depending on the way that they were published: *dynamic* services, those created by a program in execution and *static* services, created using service files. The services behave similarly without regard of the publication method, however, dynamic services are unpublished automatically when Polo is stopped or restarted (**but not when it is reloaded**) while static services last as long as the file exists.

.. _static_services:

Static services
---------------

- All files in the ``$(MARCOPOLO_DIR)/polo/services`` or ``$HOME/.polo/services`` are considered services, and are expected to have the following structure skeleton (defined in ``$(MARCOPOLO_DIR)/polo/skel``:

.. literalinclude:: ../../../marcopolo/etc/marcopolo/polo/services/skel
	:language: javascript

-- The ``id`` parameter can be any string from 1 to 30 characters long if the service is a root service. In the case of user services, the rule still applies, but the final service identifier will be ``$USER:id``.

-- The ``params`` is an JSON object of custom parameters, useful for filtering, information about the service, etc. The values of each parameter can only be basic types (no nested arrays/objects are allowed). It is an optional parameter.

-- The ``groups`` parameter is optional and specifies the groups where the service has to be published. If not supplied, the service will be published in all the multicast groups configured for the :doc:`Polo </daemons/polo>` instance. The parameter must be an array of IP strings. **Note** that only those groups where Polo is configured to work are valid, and the service will not be published in any other multicast group configured in the service file.

-- The ``disabled`` parameter is optional, and if defined and set to ``true`` will disable the service publication in all groups. Otherwise it will be ignored.	

.. _dynamic_services:

Dynamic services
----------------

The dynamic services are indistinguishable in behaviour to static services (they can even be created as static services), and are configured using the following tools:

- The :doc:`bindings </bindings/intro>` of Polo during execution time.

- The script ``poloservice`` offers an interactive method to create a service file and publish it (it uses the Polo binding underneath).
