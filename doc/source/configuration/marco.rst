Marco configuration
-------------------

The following options are configurable in the file ``/etc/marcopolo/marco/marco.conf``:

- ``RETRIES``: If the request does not find any node (or the specified amount of nodes, it will be sent again as many times as the value of the parameter. If not defined, its value is 0).

- ``TIMEOUT``: Marco will wait as much time as indicated in this parameter (in seconds, allowing decimals).

- ``MULTICAST_ADDR``: Marco will request nodes in the multicast groups indicated in this parameter (separated by commas)

- ``PORT``: The port of the groups.

- ``BINDING_PORT``: The port for the binding.