__author__ = 'martin'

DEBUG = True
PORT = 1337 # CHANGE TO POLOPORT
MARCOPORT = 1338
MULTICAST_ADDR = '224.0.0.112'
HOPS = 1
IFACE = 'eth0'

SERVICES=[
    {'id':'tomcat', 'version':'7'},
    {'id':'python', 'version':'3'},
    {'id':'CarreraREST', 'version':'1', 'type':'tomcat', 'port':8080, 'path':'/CarreraREST/rest/'},
    {'id':'NTPServer', 'type':'tomcat', 'version':'1', 'port':8080, 'path':'/NTPServer/rest'}
]

TIMEOUT = 4000.0
CONF_DIR = '/etc/marcopolo/'
SERVICES_DIR = 'polo/services/'

LOGGING_LEVEL = 'DEBUG'
LOGGING_FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
LOGGING_DIR = '/var/log/marcopolo/'
PIDFILE_POLO = '/var/run/marcopolo/polod.pid'
PIDFILE_MARCO = '/var/run/marcopolo/marcod.pid'

RETRIES = 10