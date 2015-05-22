Services
--------

The offered services may be configured in several ways:

- A file in the services/ directory with the following skeleton:
 
.. code-block:: javascript

   {
    "id":"<unique identifier>",
    "version":"<version>" //optional
    "startup-command": "<command>" //optional
    "shared-only": "<list of multicast groups separated by commas>" //optional
    "requires-auth": "<yes/no>" // Unimplemented. Some services will only be shown to authenticated requests
   }

- By using the :doc:`/bindings` of Polo during execution time.

- The script `poloservice' offers an interactive method to create a service file and publish it (it uses the Python binding underneath).
