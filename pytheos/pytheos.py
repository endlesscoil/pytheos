#!/usr/bin/env python
from . import utils
from .connection import Connection


def connect(host):
    conn = None
    port = None

    if isinstance(host, Pytheos):
        conn = host
    elif isinstance(host, tuple):
        host, port = host
    elif isinstance(host, str) and ':' in host:
        host, port = host.split(':')
        port = int(port)

    if not conn:
        conn = Pytheos(host, port)

    class _wrapper(object):
        def __enter__(self):
            self.conn = conn
            self.conn.connect()

            return self.conn

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.conn:
                self.conn.close()

    return _wrapper()

class Pytheos(object):
    def __init__(self, server=None, port=None, from_response=None):
        if from_response:
            self.location = from_response.location
            self.usn = from_response.usn
            self.st = from_response.st
            self.cache = from_response.cache

            server = utils.extract_ip(from_response.location)

        assert server is not None
        assert port is not None

        self.server = server
        self.port = port

    def connect(self):
        self._event_channel = Connection(self.server, self.port)
        self._command_channel = Connection(self.server, self.port)

        self._event_channel.connect()
        self._command_channel.connect()

        # TODO: get status

    def close(self):
        if self._event_channel:
            self._event_channel.close()

        if self._command_channel:
            self._command_channel.close()

    def call(self, group, command, **kwargs):
        assert self._command_channel is not None

        return self._command_channel.call(group, command, **kwargs)
