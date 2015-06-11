Definition of commands
----------------------

MarcoPolo works through the passing of command-like messages. The syntax of all commands is quite uniform, though several differences appear due to the particular nature of each one.

The basic structure (JSON-based) is the following:

.. code-block:: javascript

	{
	  "Command": <name>,
	  "Params": <optional, specific params>
	  "Auth": <auth token (not yet implemented)>
	}

The (so far) implemented commands are:

- **Discovery**/**Marco** (no params): A simple command to discover operating nodes on a group. The response is based on .
- **Request-for**: Request all nodes offering a certain service.
- **Service**: Requests all services offered in a certain node.

There is not a standarized format for responses (yet). However, all replies are JSON-Based and quite similar (arrays of addresses and ports and some description strings).

Future commands:

- **Advertise**
- **Join group**