#!/usr/bin/env python
# -*- coding: utf-8
from os import kill, remove
import signal
from sys import exit

PIDFILE = '/var/run/marcopolo/polod.pid'

try:
	f = open(PIDFILE, 'r')
	pid = f.read()
	f.close()
	kill(int(pid), signal.SIGUSR1)
	exit(0)
except Exception as e:
	print(e)

