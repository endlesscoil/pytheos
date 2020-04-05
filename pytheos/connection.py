#!/usr/bin/env python
from __future__ import annotations

import telnetlib
import threading

from .api.container import APIContainer


class Connection(object):
    def __init__(self, server, port, deduplicate=False):
        self.server = server
        self.port = port
        self.deduplicate = deduplicate
        self.api = APIContainer(self)

        self._lock = threading.Lock()
        self._connection = None

    def __del__(self):
        if self._connection:
            self.close()

    @property
    def lock(self):
        return self._lock

    @property
    def connected(self):
        socket = None
        if self._connection:
            socket = self._connection.get_socket()

        return socket is not None

    def connect(self):
        with self._lock:
            self._connection = telnetlib.Telnet(self.server, self.port)

    def close(self):
        with self._lock:
            self._connection.close()
            self._connection = None

    def write(self, input):
        with self._lock:
            self._connection.write(input)

    def read_until(self, target, timeout=None):
        with self._lock:
            data = self._connection.read_until(target, timeout=timeout)

        return data

    def register_for_events(self, enable=True):
        return self.api.system.register_for_change_events(enable='on' if enable else 'off')
