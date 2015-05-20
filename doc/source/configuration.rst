.. highlight:: rst
.. _toctree-directive:

Configuration
=============

The standard configuration allows MarcoPolo to run pretty much in any small network. However, there are a certain conditions which will require a little configuration by the end-user:

- Different grids on the same network: MarcoPolo is bound to a certain default multicast group (224.0.0.112). In the event that this group is already on use on the system by other MarcoPolo grid or any other application some problems may occur. Particularly on the first case, since MarcoPolo simply does not reply to any bad-formatted message (and the odds of a JSON-based multicast application running on the same address are quite small). On the file /etc/marcopolo/marcopolo.conf the parameter MULTICAST_ADDR can be set to any compatible IPv4 multicast address. (See [1]_ for a reference).

- Multiple local-area networks: Multicast packets can be routed up to a global level (if the selected group is allowed for such task). The parameter HOPS sets the TTL (Time To Live) of the package to distribute the package beyond the local designated router. **Important**: use only with a supported MULTICAST_ADDR value.

.. toctree::
	configuration/basics
	configuration/marco
	configuration/polo



.. [1] IANA Guidelines for IPv4 Multicast Address Assignments http://tools.ietf.org/html/rfc5771#page-4
