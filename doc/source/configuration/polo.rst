Polo configuration
------------------

- ``POLO_USER_DIR``: The root folder for all polo parameters (services, configuration files, etc) (by default ``/etc/marcopolo/polo``).

- ``SERVICES_DIR``: The name of the directory relative to ``POLO_USER_DIR`` (by default ``./services``)

- ``MULTICAST_ADDR``: The multicast groups to join.

- ``RETRIES``: Maximum number of retries if no multicast joining can be done (due to a network failure).

- ``HOPS``: Value of the TTL field in the messages (experimental).

- ``LOGGING_DIR``: Directory for log storage.

- ``LOG_FILE``: Name of the log file.