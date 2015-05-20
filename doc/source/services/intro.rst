Services
--------

The offered services may be configured in two ways:

- A file in the services/ directory with the following skeleton:
 
.. code-block:: javascript

   {
    "id":"<unique identifier>",
    "version":"<version>"
    "startup-command": "<command>"
    "shared-only": "<list of multicast groups separated by commas>"
    "allows-copy": "<yes/no>" //Allows copy of the .mar file
    "requires-auth": "<yes/no>" // Some services will only be shown to authenticated requests
   }

The script `poloservice' offers an interactive method to create a service file and publish it.

- By using the `register()` and `deregister()` functions during execution time.
