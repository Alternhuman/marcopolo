__author__ = 'martin'


PORT = 1337
MULTICAST_ADDR = '224.0.0.112'
IFACE = 'eth0'

SERVICES={
    'tomcat':{'id':'tomcat', 'version':'7'},
    'python3':{'id':'python', 'version':'3'},
    'CarreraREST':{'id':'CarreraREST', 'version':'1', 'type':'tomcat', 'port':8080, 'path':'/CarreraREST/rest/'},
    'NTPServer': {'id':'NTPServer', 'type':'tomcat', 'version':'1', 'port':8080, 'path':'/NTPServer/rest'}
}