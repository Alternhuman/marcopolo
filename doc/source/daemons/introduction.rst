Daemons
=======

MarcoPolo runs as two independent daemon services (aiming for the highest independence between Marco and Polo), and by default are launched during startup. The daemons are controlled through the init application (either init.d or systemd) and have no output but the log files (and, if any, the messages provided by the init process).
