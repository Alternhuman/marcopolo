import twisted.application
from twisted.application import internet
from marcopolo.marco.marcobinding import MarcoBinding
from marcopolo.marco_conf import utils
from marcopolo.marco import conf
import logging
from os import path

logging.basicConfig(filename=path.join(conf.LOGGING_DIR, 'marcod.log'), level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)
logging.info("Starting service marcod")

application = twisted.application.service.Application("Marco server")
internet.UDPServer(conf.MARCOPORT, MarcoBinding(), interface='127.0.1.1').setServiceParent(application)