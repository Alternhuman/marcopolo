import socket
import six
from six.moves import configparser
import logging
import socket
import os

LOGGING_DIR = '/var/log/marcopolo/'
LOGGING_FILENAME = "marcod.log"
LOGGING_LEVEL = 'DEBUG'
LOGGING_FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
MARCOPORT = 1338
BINDING_IFACE = '127.0.1.1'
TIMEOUT = 1000.0
MULTICAST_ADDR = '224.0.0.112'
POLOPORT = 1337 
PORT = POLOPORT
FRAME_SIZE = 4096
DEBUG = True

CONF_DIR = '/etc/marcopolo/marco'

default_values = {
    "LOGGING_DIR" : '/var/log/marcopolo/',
    "LOGGING_FILENAME" : "marcod.log",
    "LOGGING_LEVEL" : 'DEBUG',
    "LOGGING_FORMAT" : "%(asctime)s:%(levelname)s:%(message)s",
    "MARCOPORT" : 1338,
    "BINDING_IFACE" : '127.0.1.1',
    "TIMEOUT" : 1000.0,
    "MULTICAST_ADDR" : '224.0.0.112',
    "POLOPORT" : 1337,
    "PORT" : POLOPORT,
    "FRAME_SIZE" : 4096,
    "DEBUG" : True
}

config = configparser.RawConfigParser(default_values, allow_no_value=False)


MARCO_FILE_READ = os.path.join(CONF_DIR, 'marco.cfg')

try:
    with open(MARCO_FILE_READ, 'r') as f:
        config.readfp(f)
        
        DEBUG = config.getboolean('marco', 'DEBUG')
        MARCOPORT = config.getint('marco', 'MARCOPORT')
        MULTICAST_ADDR = config.get('marco', 'MULTICAST_ADDR')
        TIMEOUT = config.getfloat('marco', 'TIMEOUT')
        FRAME_SIZE = config.getint('marco', 'FRAME_SIZE')
        POLOPORT = config.getint('marco', 'POLOPORT')
        PORT = POLOPORT

        LOGGING_DIR = config.get('marco', 'LOGGING_DIR')
        LOGGING_FILENAME = config.get('marco', 'LOGGING_FILENAME')
        LOGGING_LEVEL = config.get('marco', 'LOGGING_LEVEL')
        LOGGING_FORMAT = config.get('marco','LOGGING_FORMAT')
        BINDING_IFACE = config.get('marco', 'BINDING_IFACE')
        FRAME_SIZE = config.getint('marco', 'FRAME_SIZE')

except IOError as i:
    logging.warning("Warning! The configuration file is not available. Defaults as fallback")
except Exception as e:
    logging.warning("Unknown exception in parser %s" % e)