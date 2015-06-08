#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twisted.internet import reactor, defer

import sys, logging, os, signal #time, string were necessary
from os import path, makedirs, listdir

sys.path.append('/opt/marcopolo/')
from marco_conf import utils, conf

from marcobinding import MarcoBinding

@defer.inlineCallbacks
def graceful_shutdown():
	yield logging.info('Stopping service marcod')


if __name__ == "__main__":
	signal.signal(signal.SIGHUP, signal.SIG_IGN)
	
	pid = os.getpid()
	
	if not path.exists('/var/run/marcopolo'):
		makedirs('/var/run/marcopolo')
	
	f = open(conf.PIDFILE_MARCO, 'w')
	f.write(str(pid))
	f.close()


	#logging.basicConfig(filename=conf.LOGGING_DIR+'marcod.log', level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)
	logging.basicConfig(stream=sys.stdout, level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)
	
	server = reactor.listenUDP(conf.MARCOPORT, MarcoBinding(), interface='127.0.1.1')
	reactor.run()
