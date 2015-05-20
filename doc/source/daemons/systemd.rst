Systemd-style daemons
---------------------

.. ArchLinux daemons are managed by the `systemd` utility [1]_ instead of the popular init.d-style for a series of performance and architectural reasons [2]_.


.. https://wiki.archlinux.org/index.php/Systemd

Systemd is a service and package manager for Linux which is growing on popularity (and controversy) every day. The most popular distributions implement it as of today.

Launching a daemon is achieved through Units. Units are files that defined the behaviour of a certain service, mount, device, or socket. Marco and Polo are configured as different units with the network as dependency.

