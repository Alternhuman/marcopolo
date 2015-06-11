import twisted.application
from twisted.application import internet
from marcopolo.marco.marcobinding import MarcoBinding
from marcopolo.marco_conf import utils, conf

application = twisted.application.service.Application("Marco server")
internet.UDPServer(conf.MARCOPORT, MarcoBinding(), interface='127.0.1.1').setServiceParent(application)