Fundamentals
============

MarcoPolo (named upon the swimming pool game [1]_) is a utility designed to allow hosts to publicly share their available resources (known as :doc:`services </services/intro>`) inside a local-area network. Multiple grids of nodes can work in the same network without interferences and nodes can work on different grids simultaneously.

MarcoPolo is built upon UDP multicast sockets. The multicast approach reduces the neccesary bandwith compared to broadcast messaging and makes it possible to have multiple independent grids on the same network.

The underlying architecture of the proposed implementation is defined on two independent modules, inspired on the dynamics of the Marco Polo game:

- A :doc:`/fundamentals/marco` instance, bound to each application in need of access to the protocol. It is in charge of creating commands to multicast in the network, and works pretty much like a DNS resolver.
- A :doc:`/fundamentals/polo` instance running as a daemon process listen continually for incoming multicast in a certain (configurable) group (or groups), sending responses to a request if this satisfies a set of conditions (same multicast group, request for a service which is offered by the node...).

- A set of configuration files for both modules.

- A set of service configuration files which describe the features of each service.

- All messages are codified as JSON messages and sent encoded as UTF-8 strings.

- A set of bindings for Python, C/C++ and Java.

The software is implemented on Python using Twisted [2]_ as the tool to manage the asynchronous sockets.

.. toctree::
	fundamentals/marco
	fundamentals/polo
	fundamentals/configuration_files

.. [1] http://en.wikipedia.org/wiki/Marco_Polo_%28game%29
.. [2] https://twistedmatrix.com/
