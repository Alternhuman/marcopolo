Fundamentals
============

MarcoPolo (named based on the swimming pool game [1]_) is a simple utility designed to allow hosts to publicly share their available resources (known as 'services') inside a local-area network, allowing multiple grids of nodes to work in the same net without any net interference and hosts to work on different grids simultaneously.

MarcoPolo is built upon UDP-based low-level multicast sockets. The multicast approach reduces the neccesary bandwith compared to broadcast messaging

The architecture of the system is based on two independent modules, inspired on the dynamics of the Marco Polo game:

- A **Marco** instance, bound to each application in need of access to the protocol. It is in charge of creating commands to multicast in the network, and works very much like a DNS resolver (through a local socket on 127.0.1.1).
- A **Polo** instance running as a daemon process listen continually for incoming multicast in a certain (configurable) group(s), sending responses to a request when this satisfies a set of conditions (same multicast group, request for a service which is offered by the node...).
- A set of configuration files for both roles.
- A set of service configuration files were several parameters can be specified.
- All messages are codified as JSON messages and sent encoded as UTF-8 strings.
- A set of bindings for Python, C/C++ and Java. 

.. [1] http://en.wikipedia.org/wiki/Marco_Polo_%28game%29
