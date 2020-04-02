#!/usr/bin/env python
import queue
import threading
import time

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
        self._command_channel = Connection(self.server, self.port)
        self._command_channel.connect()

        self._event_channel = Connection(self.server, self.port, deduplicate=True)
        self._event_channel.connect()
        self._event_channel.register_for_events(True)

        self._event_thread = EventThread(self._event_channel)
        self._event_thread.start()

        # TODO: get status

    def close(self):
        self._event_thread.stop()
        self._event_thread.join()

        if self._event_channel:
            self._event_channel.close()

        if self._command_channel:
            self._command_channel.close()


    def call(self, group, command, **kwargs):
        assert self._command_channel is not None

        header, payload = self._command_channel.call(group, command, **kwargs)

        return header, payload


class EventThread(threading.Thread):
    def __init__(self, conn):
        super().__init__()

        self._connection = conn
        self.running = False

    def run(self) -> None:
        self.running = True

        while self.running:
            results = self._connection.read_message()
            if results:
                print('Got event', results)
                # TODO

            time.sleep(0.01)

    def stop(self):
        self.running = False
