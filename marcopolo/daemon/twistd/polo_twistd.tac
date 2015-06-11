# -*- coding: utf-8 -*-
import twisted.application
from twisted.application import internet
from marcopolo.marco_conf import utils, conf


from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, defer

import os
from os import listdir, makedirs, path
from os.path import isfile, join
from io import StringIO

import sys, signal, json, logging
from twisted.internet.error import MulticastJoinError
import time
import pwd, grp
import re

from marcopolo.marco_conf import conf

from marcopolo.polo.polobinding import PoloBinding
from marcopolo.polo.polo import Polo
__author__ = 'Diego Martín'

application = twisted.application.service.Application("Polo server")
#internet.UDPServer(conf.MARCOPORT, MarcoBinding(), interface='127.0.1.1').setServiceParent(application)

offered_services = {}
user_services = {}

polo_instances = {}
polobinding_instances = {}

logging.basicConfig(filename=os.path.join(conf.LOGGING_DIR,'polod.log'), level=conf.LOGGING_LEVEL.upper(), format=conf.LOGGING_FORMAT)



def reload_services(sig, frame):
    """
    Captures the ``SIGUSR1`` signal and reloads the services\
    in each ``Polo`` object. The signal is ignored \
    during processing.

    :param signal sig: The signal identifier

    :param object frame: TODO
    """
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    logging.info("Broadcasting reload")
    for group, instance in polo_instances.items():
        instance.reload_services()
    signal.signal(signal.SIGUSR1, reload_services)


def graceful_shutdown():
    """
    Stops the reactor gracefully
    """
    logging.info('Stopping service polod')

def start_multicast():
    """
    Starts a :class:`Polo` instance for each multicast group configured in\ 
    conf.MULTICAST_ADDRS, initializing all the data structures
    """
    for group in conf.MULTICAST_ADDRS:
        offered_services[group] = []
        user_services[group] = {}
        polo = Polo(offered_services[group], user_services[group], group)
        polo_instances[group]=polo
        #reactor.listenMulticast(conf.PORT, polo, listenMultiple=False, interface=group)
        internet.MulticastServer(conf.PORT, polo, listenMultiple=False, interface=group).setServiceParent(application)

def start_binding():
    """
    Starts the :class:`PoloBinding`
    """
    polobinding = PoloBinding(offered_services, 
                                  user_services, 
                                  conf.MULTICAST_ADDRS
                            )
    #reactor.listenUDP(conf.POLO_BINDING_PORT, polobinding, interface="127.0.0.1")
    internet.UDPServer(conf.POLO_BINDING_PORT, polobinding, interface='127.0.1.1').setServiceParent(application)

signal.signal(signal.SIGUSR1, reload_services)

start_multicast()
start_binding()