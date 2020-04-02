#!/usr/bin/env python
import json
import telnetlib
import threading
import time

from . import utils
from .types import HEOSResult


class Connection(object):
    def __init__(self, server, port, deduplicate=False):
        self.server = server
        self.port = port
        self.deduplicate = deduplicate

        self._lock = threading.Lock()
        self._last_response = None

    def __del__(self):
        if self._connection:
            self.close()

    def connect(self):
        with self._lock:
            self._connection = telnetlib.Telnet(self.server, self.port)

    def close(self):
        with self._lock:
            self._connection.close()
            self._connection = None

    def register_for_events(self, enable=True):
        header, payload = self.call('system', 'register_for_change_events', enable='on' if enable else 'off')

        return header.succeeded

    def call(self, group, command, **kwargs):
        assert self._connection is not None

        command_string = utils.build_command_string(group, command, **kwargs)
        with self._lock:
            self._connection.write(command_string.encode('utf-8'))
        results = self.read_message()

        header = HEOSResult(from_json=results.get('heos'))
        payload = results.get('payload')

        return header, payload

    def read_message(self, timeout=1):
        response = b''
        results = None

        started = time.time()
        while True:
            with self._lock:
                response += self._connection.read_until(b'\r\n', timeout=1)

            if b"\r\n" in response:
                response = response.strip()

                if self.deduplicate and response == self._last_response:
                    response = b''
                    continue

                self._last_response = response

                try:
                    print('parsing', response)
                    results = json.loads(response.decode('utf-8'))
                except (ValueError, TypeError):
                    response = b'' # Not valid JSON; reset & retry
                    continue

                # Valid data
                break

            if time.time() - started > timeout:
                break

        return results
