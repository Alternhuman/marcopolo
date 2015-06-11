Configuration
=============

The standard configuration allows MarcoPolo to run pretty much in any small network without any configuration. However, in certain situations some parameters must be modified prior any usage.

- Different grids on the same network: MarcoPolo is bound to the multicast group ``224.0.0.112`` by default. In the event that this group is already in use by other MarcoPolo grid or any other application some problems may arise. Particularly on the first case, since MarcoPolo simply ignores any bad-formatted message (and the odds of a JSON-based mulicast application running on the same address are honestly quite small). The parameter ``MULTICAST_ADDRS`` in the file ``/etc/marcopolo/polo/polo.conf`` can be set to a list of compatible IPv4 multicast addresses.

- Multiple local-area networks: Multicast packets can be routed up to a global level (if the selected group is allowed to). The parameter HOPS in the marcopolo.conf file sets the TTL (Time To Live) of the package to distribute it beyond the local designated router. **Important**: use only with a supported ``MULTICAST_ADDRS`` value, otherwise unexpected behaviour might occur. This feature is however not well tested, and it is not guaranteed to work.

.. toctree::
	marco
	polo
	examples/index

.. [1] IANA Guidelines for IPv4 Multicast Address Assignments http://tools.ietf.org/html/rfc5771#page-4

