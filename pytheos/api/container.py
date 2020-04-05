#!/usr/bin/env python
from __future__ import annotations

import json
import time

from pytheos import utils
from pytheos.api.player.player import PlayerAPI
from pytheos.api.system import SystemAPI
from pytheos.errors import CommandFailedError
from pytheos.types import HEOSResult


class APIContainer(object):
    def __init__(self, connection):
        self.system = SystemAPI(connection)
        self.player = PlayerAPI(connection)

        self._connection = connection
        self._last_response = None

    def call(self, group, command, **kwargs) -> HEOSResult:
        assert self._connection is not None

        self.send_message(group, command, **kwargs)
        message = self.read_message()
        results = HEOSResult(message)

        if results.result is None:
            raise CommandFailedError('No "result" found in "heos" response', results)

        if results.result == 'fail':
            raise CommandFailedError('Failed to execute command', results)

        return results

    def send_message(self, group, command, **kwargs):
        command_string = utils.build_command_string(group, command, **kwargs)
        self._connection.write(command_string.encode('utf-8'))

    def read_message(self, timeout=1, delimiter=b'\r\n'):
        results = None
        response = b''

        started = time.time()
        while True:
            response += self._connection.read_until(delimiter, timeout=1) # FIXME: do something about this hardcoded timeout

            if delimiter in response:
                response = response.strip()

                # Bail out if we got a duplicate message and have deduplicate enabled
                if self._connection.deduplicate and response == self._last_response:
                    response = b''
                    continue
                self._last_response = response

                # Confirm message is valid JSON
                try:
                    results = json.loads(response.decode('utf-8'))
                except (ValueError, TypeError):
                    response = b'' # Not valid JSON; reset & retry
                    continue

                # Valid data
                break

            # And break out if we exceeded our time limit to read a valid message
            if time.time() - started > timeout:
                break

        return results
