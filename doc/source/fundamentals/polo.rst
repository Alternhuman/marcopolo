Polo
====

**Polo** is in charge of publishing the offered services. It handles all the services that are to be published and replies to the requests which satisfy the defined criteria. Polo publishes both root and user services (see :doc:`/services/intro`) and can work simultaneously in more than one group without interferences between them.

In the proposed implementation there are two main types of services: :ref:`*static*<static_services>` and :ref:`*dynamic*<dynamic_services>` ones. The *static* services are always published and are stored as JSON-serialized files with all the required parameters and are loaded on startup. The published services can be reloaded during execution time. The *dynamic* ones are published using the :doc:`*bindings*</bindings/intro>` and are only published during the execution of the polo instance.

In addition to that, the services can be classified as *root* services (services for the whole system) and *user* services, managed by any user. Both types behave similarly, existing only a restriction for user services: the id of the service will always have the following syntax: ``<username>``:``<desired id>``.
