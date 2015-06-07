Marco
=====

**Marco** is in charge of the service discovering (leaving to **Polo** all the tasks related to service publishing). The underlying principle for all commands is sending datagrams to the configured multicast address (or addresses) requesting information, and awaiting a certain time for a set of responses (which can range from 1 to unlimited, depending on the type of the request). When the time is over, the collected results are returned to the requesting program or user.

A datagram example is the following:

.. code-block:: JavaScript

	{
		"Command":"Request-For",
		"Params":"statusmonitor"
	}

All messages are JSON-formatted and UTF-8 encoded. Currently there is no support for fragmentation, so the messages must be less than 2048 bytes long.

When a **Request-For** message like the one in the example is received by the **Polo** instance, a reply is issued only if the service is configured to be published. Otherwise no response will be made. The **Marco** instance will wait for a configurable amount of time, and return the received responses when the timeout is triggered. There are several parameters which modify this default behaviour, such as retries or timeout modification.

All requests are subject to customization through a series of parameters. Those can restrict the maximum number of responses, a exclusion policy or even override configuration parameters such as retries or waiting timeout. The commands are defined in the :doc:`/commands/intro` section.