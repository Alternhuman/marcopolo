Daemons
=======

MarcoPolo runs as two independent daemon services (aiming for the total independence between Marco and Polo) and are launched during startup. The daemons are controlled through the system daemon manager (either ``init`` or ``systemd``). All the relevant output is written in serveral log files (and, if any, the messages provided by the daemon manager).

.. toctree::
	systemv
	systemd

MarcoPolo runs as two independent daemon services (for the Marco and Polo functionality to be completely independent)

ArchLinux daemons are managed by the `systemd` utility [1]_ instead of the popular init.d-style daemons. 


.. [1] https://wiki.archlinux.org/index.php/Systemd
