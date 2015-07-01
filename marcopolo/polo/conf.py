import socket
import logging
import os
import json

import six
from six.moves import configparser

MULTICAST_ADDRS = ['224.0.0.112', '224.0.0.113']

PORT = 1337 # CHANGE TO POLOPORT
SECRET_FILE = '/etc/marcopolo/polo/secret'

SECRET_RENAME = 'V33YJFtywVmSKDvbQQsz6ZEmDkhleWEJ'

POLO_BINDING_PORT = 1390
LOGGING_LEVEL = 'DEBUG'
LOGGING_FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
LOGGING_DIR = '/var/log/marcopolo/'
LOGGING_FILE = 'polod.log'

VERIFY_REGEXP = '^([\d\w]+):([\d\w]+)$'
MULTICAST_ADDR_FALLBACK = '224.0.0.112'
#CONF_DIR = '/etc/marcopolo/'
SERVICES_DIR = 'services/'

POLO_USER_DIR = ".polo"

DEBUG = True
HOPS = 1
RETRIES = -10
POLO_PARAMS = {"hostname":socket.gethostname()}
GROUP_NAME = "marcopolo"

FRAME_SIZE = 4096

CONF_DIR = '/etc/marcopolo/polo'

default_values = {
    "MULTICAST_ADDRS" : ['224.0.0.112', '224.0.0.113'],
    "PORT" : 1337,
    "SECRET_FILE" : '/etc/marcopolo/polo/secret',
    "SECRET_RENAME" : 'V33YJFtywVmSKDvbQQsz6ZEmDkhleWEJ',
    "POLO_BINDING_PORT" : 1390,
    "LOGGING_LEVEL" : 'DEBUG',
    "LOGGING_FORMAT" : '%(asctime)s:%(levelname)s:%(message)s',
    "LOGGING_DIR" : '/var/log/marcopolo/',
    "LOGGING_FILE" : 'polod.log',
    "VERIFY_REGEXP" : '^([\d\w]+):([\d\w]+)$',
    "MULTICAST_ADDR_FALLBACK" : '224.0.0.112',
    "CONF_DIR" : '/etc/marcopolo/polo',
    "SERVICES_DIR" : 'services/',
    "POLO_USER_DIR" : ".polo",
    "DEBUG" : True,
    "HOPS" : 1,
    "RETRIES" : -10,
    "POLO_PARAMS" : {"hostname":socket.gethostname()},
    "GROUP_NAME" : "marcopolo",
    "FRAME_SIZE" : 4096
}

config = configparser.RawConfigParser(default_values, allow_no_value=False)

POLO_FILE_READ = os.path.join(CONF_DIR, 'polo.cfg')


try:
    with open(POLO_FILE_READ, 'r') as f:
        config.readfp(f)
        
        DEBUG = config.getboolean('polo', 'DEBUG')

        MULTICAST_ADDRS = config.get('polo', 'MULTICAST_ADDRS').split()
        PORT = config.getint('polo', 'PORT')
        SECRET_FILE = config.get('polo', 'SECRET_FILE')
        
        POLO_BINDING_PORT = config.getint('polo', 'POLO_BINDING_PORT')
        LOGGING_LEVEL = config.get('polo', 'LOGGING_LEVEL')

        LOGGING_FORMAT = config.get('polo', 'LOGGING_FORMAT')
        LOGGING_DIR = config.get('polo', 'LOGGING_DIR')
        LOGGING_FILE = config.get('polo', 'LOGGING_FILE')
        VERIFY_REGEXP = config.get('polo', 'VERIFY_REGEXP')
        MULTICAST_ADDR_FALLBACK = config.get('polo', 'MULTICAST_ADDR_FALLBACK')
        MULTICAST_ADDR = MULTICAST_ADDR_FALLBACK

        SERVICES_DIR = config.get('polo', 'SERVICES_DIR')
        POLO_USER_DIR = config.get('polo', 'POLO_USER_DIR')
        HOPS = config.getint('polo', 'HOPS')
        RETRIES = config.getint('polo', 'RETRIES')
        GROUP_NAME = config.get('polo', 'GROUP_NAME')
        FRAME_SIZE = config.getint('polo', 'FRAME_SIZE')
    
        POLO_PARAMS = json.loads(config.get('polo', 'POLO_PARAMS'))
    

except IOError as i:
    logging.warning("Warning! The configuration file is not available. Defaults as fallback")
except Exception as e:
    logging.warning("Unknown exception in polo parser %s" % e)