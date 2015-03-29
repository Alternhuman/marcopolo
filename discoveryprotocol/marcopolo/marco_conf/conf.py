__author__ = 'martin'


PORT = 1337
MULTICAST_ADDR = '224.0.0.112'
IFACE = 'eth0'

SERVICES=[
    {'id':'tomcat', 'version':'7'},
    {'id':'python', 'version':'3'},
    {'id':'CarreraREST', 'version':'1', 'type':'tomcat', 'port':8080, 'path':'/CarreraREST/rest/'},
    {'id':'NTPServer', 'type':'tomcat', 'version':'1', 'port':8080, 'path':'/NTPServer/rest'}
]

TIMEOUT = 2