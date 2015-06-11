Marcoinstallkey
===============

The utility detects all nodes in the network and install the specified public key in them. This is useful when deploying ssh-based applications such as MPI, avoiding entering the password every time.

If run with the -h, a help message is displayed
::

	>  Usage: marcoinstallkey [-h|-n] [-i [identity_file]] [-p port] [[-o <ssh -o options>] ...] [-u user]\n
	
	Arguments
	 -h, --help	show this help message and exit
	 -i [identity_file]   Use only the key(s) contained in identity_file (rather than looking for identities via ssh-add(1) or in the default_ID_file).
	                      If the filename does not end in .pub this is added. If the filename is omitted, the default_ID_file is used.
	                      Note that this can be used to ensure that the keys copied have the comment one prefers and/or extra options applied,
	                      by ensuring that the key file has these set as preferred before the copy is attempted.
	 -p [port]
	 -o [ssh_option]
	 -n                   dry run
	 -u                   user
