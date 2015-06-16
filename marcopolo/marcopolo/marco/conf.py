import socket
import six
from six.moves import configparser
import logging

DEBUG = True
MARCOPORT =1338
MULTICAST_ADDR = '224.0.0.112'
TIMEOUT =1000.0
FRAME_SIZE =4096
POLOPORT = 1337 

default_values = {
	'DEBUG': DEBUG,
	'MARCOPORT': MARCOPORT, # TODO: Move to general configuration file
	'MULTICAST_ADDR': MULTICAST_ADDR,
	'TIMEOUT': TIMEOUT,
	'FRAME_SIZE': FRAME_SIZE,
	'POLOPORT': POLOPORT # TODO: Move to general configuration file
}

config = configparser.SafeConfigParser(default_values, allow_no_value=False)

MARCO_FILE_READ = '/etc/marcopolo/marco/marco.conf'

try:
	with open(MARCO_FILE_READ, 'r') as f:
		config.readfp(f)
		
		DEBUG = config.getboolean('marco', 'DEBUG')
		MARCOPORT = config.getint('marco', 'MARCOPORT')
		MULTICAST_ADDR = config.get('marco', 'MULTICAST_ADDR')
		TIMEOUT = config.getint('marco', 'TIMEOUT')
		FRAME_SIZE = config.getint('marco', 'FRAME_SIZE')
		POLOPORT = config.getint('marco', 'POLOPORT')
		PORT = POLOPORT
except IOError as i:
	logging.warning("Warning! The configuration file is not available. Defaults as fallback")