#!/usr/bin/env python
import telnetlib

from . import utils


class Connection(object):
    def __init__(self, server, port):
        self.server = server
        self.port = port

    def __del__(self):
        if self._connection:
            self.close()

    def connect(self):
        self._connection = telnetlib.Telnet(self.server, self.port)

    def close(self):
        self._connection.close()
        self._connection = None

    def call(self, group, command, **kwargs):
        assert self._connection is not None

        command_string = utils.build_command_string(group, command, **kwargs)

        self._connection.write(command_string.encode('ascii'))

        response = b''
        while True:
            response += self._connection.read_some()
            if b"\r\n" in response:
                response = response.strip()
                break

            # FIXME: Add timeout.

        return response
