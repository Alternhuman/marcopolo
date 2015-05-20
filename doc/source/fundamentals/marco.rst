Marco
----

**Marco** is in charge of all the functionality regarding service discovery (leaving to **Polo** all the tasks related to service publishing). The basic principle is sending datagrams to the configured multicast address (or addresses) requesting information, and awaiting a certain time for a set of responses (which can range from 1 to unlimited, depending on the type of the request). When the time is over, the collected results are returned to the program that requested them.

The commands are defined in the :doc:`/commands` section.

All requests are subject to customization through a series of parameters. Those can restrict the maximum number of responses, a exclusion policy or even override configuration parameters such as retries or timeout.
