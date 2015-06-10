import sys, logging, os, signal
from polod import reload_services
from twisted.internet import reactor, defer

def main(args=None):
	if args is None:
		args = sys.argv[1:]

	pid = os.getpid()
	
	if not path.exists('/var/run/marcopolo'):
		makedirs('/var/run/marcopolo')
	
	f = open(conf.PIDFILE_POLO, 'w')
	f.write(str(pid))
	f.close()

	signal.signal(signal.SIGHUP, signal.SIG_IGN)
	signal.signal(signal.SIGUSR1, reload_services)
	
	logging.basicConfig(filename=conf.LOGGING_DIR+'polod.log', level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)

	reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
	reactor.callWhenRunning(start_multicast)
	reactor.callWhenRunning(start_binding)
	reactor.run()