Bindings
========

Applications on a node can get access to the Marco and Polo functionality through a series of functions available on a set of bindings and shell commands. The main functionality of those bindings is dedicated to the discovery of nodes. Nonetheless, some other information has also been made available.

There are three bindings for three different languages: C++ (C compatible), Python and Java, offering the same functionality in the same fashion, yet taking advantage of the particular features of each languaje.

The bindings are inspired by the netdb.h functions used in order to resolve host and DNS names, and as such they communicate with the local Marco or Polo instance through local sockets (on 127.0.1.1 port 1337 and 1338).

For the sake of consistency with the usual Marco Polo commands, all data is encoded in UTF-8 JSON strings with a similar structure.

All bindings implement this set of functions:

.. toctree::
	:maxdepth: 2

	marco
	polo