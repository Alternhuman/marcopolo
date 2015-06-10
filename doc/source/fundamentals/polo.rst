Polo
====

**Polo** is in charge of publishing the offered services. It handles all the services that are to be published and replies to the requests which satisfy the defined criteria. Polo publishes both root and user services (see :doc:`/services/intro`) and can work simultaneously in more than one group without interferences between them.

..In the proposed implementation, all services are JSON-encoded strings with all the parameters, and the publication follows the same approach as other products such as the Apache HTTP Server, using two folders (services and services-published). The service list can be updated during execution time.

..In addition to that method, users can publish services using the :doc:`/bindings/intro` present on several programming languages. The only disadvantage of this method is persistence: the services are only available during the execution (there are plans to integrate ~/.polo, but that is not yet ready) and have to follow more strict name rules (basically, all services are formatted as <username>:<service_name>).
