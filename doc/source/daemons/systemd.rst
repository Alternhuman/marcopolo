Systemd-style daemons
---------------------

Systemd is a service and package manager for Linux which is growing on popularity (and controversy) every day. The most popular distributions implement it as of today.

Launching a daemon is achieved through Units. Units are files that defined the behaviour of a certain service, mount, device, or socket. Marco and Polo are configured as different units with some dependencies.

Both daemons require a connection to work, so both will have the dependencies ``network.target network-online.target`` to wait for the network functionality to be loaded and ``sys-subsystem-net-devices-net0.device`` to wait for the main interface to be configured before starting to work.

Python 2 units
~~~~~~~~~~~~~~

In Python 2 the daemon management is done by ``twistd``.

Marco unit

.. literalinclude:: ../../../marcopolo/daemon/marcod.service

Polo unit

.. literalinclude:: ../../../marcopolo/daemon/polod.service

Python 3 units
~~~~~~~~~~~~~~

In Python 3 the daemon is configured manually.

Marco unit

.. literalinclude:: ../../../marcopolo/daemon/python3/marcod.service

Polo unit

.. literalinclude:: ../../../marcopolo/daemon/python3/polod.service