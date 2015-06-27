#!/usr/bin/env python3
# -*- coding: utf-8
from os import kill, remove
import os, signal
BINARY = '/opt/marcopolo/marco/marcod.py'
PIDFILE = '/var/run/marcopolo/marcod.pid'

try:
	f = open(PIDFILE, 'r')
	pid = f.read()
	f.close()
	kill(int(pid), signal.SIGTERM)
	os.remove(PIDFILE)
except Exception as e:
	print(e)