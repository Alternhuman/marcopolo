#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
from twisted.internet import reactor, defer, ssl
from twisted.internet.error import MulticastJoinError
from twisted.internet.protocol import Factory, Protocol
from OpenSSL import SSL

import os

import sys, signal, logging

from marcopolo.polo import conf
from marcopolo.polo.polobindingssl import PoloBindingSSL, PoloBindingSSLFactory
from marcopolo.polo.polo import Polo

__author__ = 'Diego Martín'

offered_services = {}
user_services = {}

polo_instances = {}
polobinding_instances = {}


def reload_services(sig, frame):
    """
    Captures the ``SIGUSR1`` signal and reloads the services\
    in each ``Polo`` object. The signal is ignored \
    during processing.

    :param signal sig: The signal identifier

    :param object frame: The current stack frame

    .. seealso signal.signal
    """
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    logging.info("Broadcasting reload")
    for _, instance in polo_instances.items():
        instance.reload_services()
    signal.signal(signal.SIGUSR1, reload_services)


# def sigint_handler(signal, frame):
#     """
#     A ``SIGINT`` handler.

#     :param signal sig: The signal identifier

#     :param object frame:
#     """
#     reactor.stop()
#     sys.exit(0)

@defer.inlineCallbacks
def graceful_shutdown():
    """
    Stops the reactor gracefully
    """
    yield logging.info('Stopping service polod')

def start_multicast():
    """
    Starts a :class:`Polo` instance for each multicast group configured in\
    conf.MULTICAST_ADDRS, initializing all the data structures
    """
    for group in conf.MULTICAST_ADDRS:
        offered_services[group] = []
        user_services[group] = {}
        polo = Polo(offered_services[group], user_services[group], group)
        polo_instances[group] = polo
        reactor.listenMulticast(conf.PORT,
                                polo,
                                listenMultiple=False,
                                interface=group)


def verifyCallback():
    print("Not verified")


def start_binding():
    """
    Starts the :class:`PoloBinding`
    """
    try:
        with open(conf.SECRET_FILE, 'r') as sf:
            secret = sf.read()
    except Exception:
        logging.error("Could not parse secret file: %s. Binding will not start" % s)
        return

    polobinding = PoloBindingSSL

    factory = PoloBindingSSLFactory(secret, offered_services, user_services, conf.MULTICAST_ADDRS)
    factory.protocol = polobinding
    
    myContextFactory = ssl.DefaultOpenSSLContextFactory(
        '/etc/marcopolo/certs/polossl.key', '/etc/marcopolo/certs/polossl.crt'
        )

    ctx = myContextFactory.getContext()

    reactor.listenSSL(conf.POLO_BINDING_PORT,
                        factory,
                        myContextFactory,
                        interface='127.0.0.1')

def main(args=None):
    """
    Starts the daemon.

    :param list args: List of the console parameters
    """
    if args is None:
        args = sys.argv[1:]

    pid = os.getpid()
    logging.basicConfig(filename=os.path.join(conf.LOGGING_DIR, 'polod.log'),
                        level=conf.LOGGING_LEVEL.upper(),
                        format=conf.LOGGING_FORMAT)

    #try:
    #    f = open(conf.PIDFILE_POLO, 'w')
    #    f.write(str(pid))
    #    f.close()
    #except Exception as e:
    #    logging.error(e)
    #    sys.exit(1)

    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGUSR1, reload_services)
    
    reactor.addSystemEventTrigger('before', 'shutdown', graceful_shutdown)
    reactor.callWhenRunning(start_multicast)
    reactor.callWhenRunning(start_binding)
    reactor.run()

if __name__ == "__main__":
    main(args=sys.argv[1:])
