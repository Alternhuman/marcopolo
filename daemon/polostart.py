#!/usr/bin/env python
# -*- coding: utf-8
import subprocess
from os import path, makedirs, devnull

BINARY = '/opt/marcopolo/polo/polod.py'
PIDFILE = '/var/run/marcopolo/polod.pid'
FNULL = open(devnull, 'w')

pid = subprocess.Popen(BINARY, stdout=FNULL, stdin=FNULL, stderr=FNULL).pid
if not path.exists('/var/run/marcopolo'):
  makedirs('/var/run/marcopolo')
f = open(PIDFILE, 'w')
f.write(str(pid))
f.close()
