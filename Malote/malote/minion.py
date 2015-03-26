#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import io
import shlex
import sys
import requests
import shutil
import json
import logging
import ssl
from subprocess import Popen
from subprocess import TimeoutExpired
from zipfile import ZipFile
from tornado.web import RequestHandler, Application, asynchronous
from tornado.httpserver import HTTPServer
from tornado.log import app_log, gen_log
from requests.exceptions import RequestException
from tornado.ioloop import IOLoop
from time import time, sleep
from collections import namedtuple
from functools import partial
from malote.util import NotCheckingHostnameHTTPAdapter, require_cert
from minion_conf import config

# Create a requests session with hostname checking disabled
# (certificates are still checked)
websession = requests.session()
websession.mount('https://', NotCheckingHostnameHTTPAdapter())

io_loop = IOLoop.instance()
processes = set()
http_cert = (config.CERT_FILE, config.KEY_FILE)

def join(processes, timeout):
    t = time()
    for proc in processes:
        proc.wait(timeout - (time() - t))

def malote_url(path):
    return 'https://%s:%d/%s' % (config.MALOTE_ADDR,
                                 config.MALOTE_PORT,
                                 path)

def http_die(message, exception):
    print("%s: %s" % (message, exception), file=sys.stderr)
    if hasattr(exception, 'response') and exception.response is not None:
        print(exception.response.text, file=sys.stderr)
    sys.exit(1)

def register():
    try:
        url = malote_url('minions')
        response = websession.post(url, params={'port': config.PORT},
                                   cert=http_cert,
                                   verify=config.MALOTE_CERT_FILE)
        response.raise_for_status()
    except requests.RequestException as err:
        http_die("Registration failed", err)

    data = response.json()
    print("Registration complete: I'm %s" % data['name'])

def unregister():
    try:
        url = malote_url('minions?port=%d' % config.PORT)
        response = websession.delete(url, cert=http_cert,
                                     verify=config.MALOTE_CERT_FILE)
        response.raise_for_status()
        print("Unregistered.")
    except requests.RequestException as err:
        http_die("Failed to unregister from Malote", err)

class DeployHandler(RequestHandler):
    @require_cert
    def post(self):
        app_log.info("Received deploy command, terminating old processes...")

        for proc in processes:
            app_log.info("Sending SIGTERM to %d" % proc.pid)
            proc.terminate()

        try:
            join(processes, 3)
        except TimeoutExpired:
            app_log.info("Old processes still alive after timeout, reaching " \
                         "the shotgun...")
            for proc in processes:
                app_log.info("Sending SIGKILL to %d" % proc.pid)
                proc.kill()
            join(processes, 1)

        processes.clear()
        app_log.info("Old processes terminated. Uncompressing new software...")

        try:
            shutil.rmtree(config.ASSETS_DIR)
        except OSError:
            pass

        file = io.BytesIO(self.request.files['assets'][0]['body'])
        with ZipFile(file) as zip:
            zip.extractall(config.ASSETS_DIR)

        with open('/tmp/estado_sc', 'w') as f:
            f.write('vacía')

        commands = json.loads(self.get_body_argument('commands'))
        for command in commands:
            proc = Popen(shlex.split(command), cwd=config.ASSETS_DIR)
            app_log.info("Ran command: %s" % command)
            processes.add(proc)


application = Application([
    ('/deploy', DeployHandler),
])

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Servidor maestro")
    parser.add_argument("-p", "--port", type=int, dest='port', 
                        default=config.PORT)
    parser.add_argument("-ma", "--malote-addr", dest='malote_addr',
                        default=config.MALOTE_ADDR)
    parser.add_argument("-mp", "--malote-port", type=int, dest='malote_port',
                        default=config.MALOTE_PORT)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    config.PORT = args.port
    config.MALOTE_ADDR = args.malote_addr
    config.MALOTE_PORT = args.malote_port

    register()

    http_server = HTTPServer(application, ssl_options={
        "certfile": config.CERT_FILE,
        "keyfile": config.KEY_FILE,
        "cert_reqs": ssl.CERT_OPTIONAL,
        "ca_certs": config.MALOTE_CERT_FILE,
    })
    http_server.listen(config.PORT, address='0.0.0.0')
    print("Minion is listening on port %d" % config.PORT)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        # Terminar cuando el usuario pulse Ctrl+C
        unregister()
