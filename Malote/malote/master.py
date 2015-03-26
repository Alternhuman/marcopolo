#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
from __future__ import absolute_import

import shutil
import sys
import ssl
import requests
import json
import logging
import random
from os.path import dirname, join
from tornado.web import RequestHandler, Application, asynchronous, \
                        StaticFileHandler
from tornado.httpserver import HTTPServer
from tornado.log import app_log, gen_log
from requests.exceptions import RequestException
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
from time import time, sleep
from collections import namedtuple
from functools import partial
from malote_conf import config
from tempfile import gettempdir
from functools import wraps
from hmac import compare_digest
from requests_futures.sessions import FuturesSession
from malote.util import NotCheckingHostnameHTTPAdapter, require_cert
from malote.goth_empire import kings

base_path = dirname(__file__)

http_cert = (config.CERT_FILE, config.KEY_FILE)
futures_session = FuturesSession()
futures_session.mount('https://', NotCheckingHostnameHTTPAdapter())

class State:
    def __init__(self):
        self.minions = set()
        self.gui_connections = set()
        self.deploying = False
        self.pending_minions = set()
    
state = State()

def set_callback(future, callback, *args, **kwargs):
    """
    Hook a future like those used in requests-futures into Tornado IO Loop.

    The callback will be executed on the next iteration of the IO loop after
    the request has been responded.

    The callback will receive the response as an argument, and optionally other
    arguments specified on this call.
    """

    def _add_callback(future):
        if future.cancelled():
            raise RuntimeError

        response = future.result(timeout=0)
        io_loop.add_callback(lambda: callback(response, *args, **kwargs))

    future.add_done_callback(_add_callback)
    
class NoItem(Exception):
    pass

class TooManyItems(Exception):
    pass

def one(iterable):
    found = False

    for item in iterable:
        if not found:
            found = True
        else:
            raise TooManyItems

    if found:
        return item
    else:
        raise NoItem

class Minion:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        current_names = set(minion.name for minion in state.minions)
        self.name = random.choice(list(kings - current_names))

    def jsonify(self):
        return {
            'ip': self.ip,
            'port': self.port,
            'name': self.name
        }


class ControlHandler(WebSocketHandler):
    def open(self):
        state.gui_connections.add(self)
        for minion in state.minions:
            self.write_json(self.enter_message(minion))

    def on_message(self, msg):
        pass
    
    def on_close(self):
        state.gui_connections.remove(self)

    def write_json(self, msg):
        self.write_message(json.dumps(msg))

    def enter_message(self, minion):
        return {
            'type': 'minion_enter',
            'data': minion.jsonify()
        }

    def leave_message(self, minion):
        return {
            'type': 'minion_leave',
            'data': minion.jsonify()
        }
    

def add_minion(minion):
    state.minions.add(minion)
    for conn in state.gui_connections:
        conn.write_json(conn.enter_message(minion))

def remove_minion(minion):
    for conn in state.gui_connections:
        conn.write_json(conn.leave_message(minion))
    state.minions.remove(minion)

class MinionsHandler(RequestHandler):
    @require_cert
    def post(self):
        ip = self.request.remote_ip
        port = int(self.get_query_argument('port'))

        if any(minion.ip == ip and minion.port == port
               for minion in state.minions):
            self.set_status(400)
            self.write({"msg": "Minion already registered"})
            return

        minion = Minion(ip, port)
        add_minion(minion)

        app_log.info("Registered minion: %s:%d" % (ip, port))

        self.write({
            "name": minion.name
        })
     
    @require_cert
    def delete(self):
        ip = self.request.remote_ip
        port = int(self.get_query_argument('port'))

        for minion in state.minions:
            if minion.ip == ip and minion.port == port:
                remove_minion(minion)
                app_log.info("Unregistered minion: %s:%d" % (ip, port))

                self.set_status(202)
                break
        else:
            app_log.warning("Attempt to unregister a non-registered minion: " +
                            "%s:%d" % (ip, port))
            self.set_status(400)
            self.write({"msg": "Not registered"})

    def check_xsrf_cookie(self):
        # These endpoints are XSRF exempt, as they can never be called 
        # in-browser
        pass


class DeployHandler(RequestHandler):
    def post(self):
        if not is_authenticated(self):
            self.set_status(403)
            self.write({"msg": "Not authorized"})
            return
        elif state.deploying:
            self.set_status(400)
            self.write({"msg": "Already deploying"})
            return

        data = json.loads(self.request.body.decode())

        archive_path = join(gettempdir(), 'malote_project')
        shutil.make_archive(archive_path, 'zip',
                            data['project_path'])
        archive_path += ".zip"

        # Sanitize input: check all minions exist
        minion_commands = {}
        for minion_key, commands in data['minion_commands'].items():
            ip, port = minion_key.split(':')
            port = int(port)

            try:
                minion = one(m for m in state.minions
                             if m.ip == ip and m.port == port)
            except NoItem:
                self.set_status(400)
                self.write({"msg": "Non existing minion: %s:%d" % (ip, port)})
                return

            minion_commands[minion] = commands

        # Now that we know the request is fine, fire the updates... if any
        if len(minion_commands) == 0:
            return

        state.deploying = True
        state.remaining_minions = set(minion_commands.keys())
        for minion, commands in minion_commands.items():
            url = 'https://%s:%d/deploy' % (minion.ip, minion.port)
            future = futures_session.post(url, files={
                    'assets': open(archive_path, 'rb')
                }, data={
                    'commands': json.dumps(commands)
                }, cert=http_cert, verify=config.MINION_CERT_FILE)
            set_callback(future, self.deployed_on_minion, minion=minion)
            app_log.info("Sent deploy command to %s:%d." % 
                         (minion.ip, minion.port))

    def deployed_on_minion(self, response, minion):
        minion_str = "%s:%d" % (minion.ip, minion.port)
        if response.ok:
            app_log.info("Deployed on %s." % minion_str)
        else:
            app_log.error("Failed to deploy on %s: %s" %
                          (minion_str, response.text))

        state.remaining_minions.remove(minion)
        if len(state.remaining_minions) == 0:
            state.deploying = False

class HomeView(StaticFileHandler):
    def initialize(self):
        super().initialize(path=static_path, default_filename='index.html')
    
    def get(self):
        # Set XSRF token
        self.xsrf_token
        # Return index.html from static path
        super().get('')

def is_authenticated(handler):
    raw_passport = handler.get_secure_cookie('session')
    if not raw_passport:
        return False
    passport = json.loads(raw_passport.decode())
    if passport['ip'] != handler.request.remote_ip:
        return False
    if passport['expires'] < time():
        return False
    return True

class AuthHandler(RequestHandler):
    def get(self):
        self.write({
            "authenticated": is_authenticated(self)
        })

    def post(self):
        data = json.loads(self.request.body.decode())
        password = data['password']
        if compare_digest(password, config.PASSWORD):
            self.set_status(202)
            self.authenticate()
        else:
            self.set_status(403)
            self.write({"msg": "Bad password"})

    def authenticate(self):
        passport = json.dumps({
            "ip": self.request.remote_ip,
            "expires": time() + 3600 * 4, # 4 hours
        })
        self.set_secure_cookie('session', passport)
        
io_loop = IOLoop.instance()

static_path = join(base_path, '../gui/dist')
application = Application([
    ('/auth', AuthHandler),
    ('/minions', MinionsHandler),
    ('/deploy', DeployHandler),
    ('/ws', ControlHandler),
    ('/', HomeView),
], **{
    'debug': True,
    'static_path': static_path,
    'xsrf_cookies': True,
    'cookie_secret': config.COOKIE_SIGN_KEY,
})

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Malote Server")
    parser.add_argument("-p", "--port", type=int, dest='port', 
                        default=config.PORT)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    config.PORT = args.port

    http_server = HTTPServer(application, ssl_options={
        "certfile": config.CERT_FILE,
        "keyfile": config.KEY_FILE,
        "cert_reqs": ssl.CERT_OPTIONAL,
        "ca_certs": config.MINION_CERT_FILE,
    })
    http_server.listen(config.PORT, address='0.0.0.0')
    print("Malote Server is listening on port %d." % config.PORT)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        # Terminar cuando el usuario pulse Ctrl+C
        pass
