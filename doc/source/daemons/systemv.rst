System V
--------

MarcoPolo is compatible with init.d scripts so it can be used in any OS which uses init.d as init process.

In Python 2 ``twistd`` will be used to manage the daemons. In Python 3 the daemons are configured manually. The dependency management is also delegated to the instances of the daemons.