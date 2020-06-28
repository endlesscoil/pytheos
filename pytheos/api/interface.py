#!/usr/bin/env python
""" Provides the APIInterface implementation """

from __future__ import annotations

import json
import time
import logging
from typing import Optional

from pytheos import utils
from pytheos.api.browse.browse import BrowseAPI
from pytheos.api.group.group import GroupAPI
from pytheos.api.player.player import PlayerAPI
from pytheos.api.system import SystemAPI
from pytheos.errors import CommandFailedError
from pytheos.types import HEOSResult

logger = logging.getLogger(__name__)


class APIInterface:
    """ Container class for raw command functionality and object references to the API groups """

    def __init__(self, connection):
        self.system = SystemAPI(self)
        self.player = PlayerAPI(self)
        self.group = GroupAPI(self)
        self.browse = BrowseAPI(self)

        self._connection: 'Connection' = connection
        self._last_response: Optional[str] = None

    def call(self, group: str, command: str, **kwargs: dict) -> HEOSResult:
        """ Formats a HEOS API request, submits it, and reads the response.

        :param group: Group name (e.g. system, player, etc)
        :param command: Command name (e.g. heart_beat_
        :param kwargs: Any parameters that should be sent along with the command
        :raises: AssertionError, CommandFailedError
        :return: HEOSResult
        """
        assert self._connection is not None

        self.send_command(group, command, **kwargs)
        message = self.read_message()
        results = HEOSResult(message)

        if results.header:
            if results.header.result is None:
                raise CommandFailedError('No "result" found in "heos" response', results)

            if results.header.result == 'fail':
                raise CommandFailedError('Failed to execute command', results)

        return results

    def send_command(self, group: str, command: str, **kwargs: dict) -> None:
        """ Formats a HEOS API request and submits it

        :param group: Group name (e.g. system, player, etc)
        :param command: Command name (e.g. heart_beat)
        :param kwargs: Any parameters that should be sent along with the command
        :raises: AssertionError, CommandFailedError
        :return: HEOSResult
        """
        command_string = utils.build_command_string(group, command, **kwargs)
        self._connection.write(command_string.encode('utf-8'))
        logger.debug(f"Sending command: {command_string.rstrip()}")

    def read_message(self, timeout: int=1, delimiter: bytes=b'\r\n') -> Optional[bytes]:
        """ Reads a message from the connection

        :param timeout: Timeout (seconds)
        :param delimiter: Message delimiter
        :return: bytes
        """
        results = None
        response = b''

        started = time.time()
        while True:
            response += self._connection.read_until(delimiter, timeout=1) # FIXME: do something about this hardcoded timeout

            if delimiter in response:
                response = response.strip()
                logger.debug(f"Got response: {response}")

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

                if "command under process" in results['heos'].get('message', ''):
                    logger.debug("Delayed - command under process")
                    response = b''
                    continue

                # Valid data
                break

            # And break out if we exceeded our time limit to read a valid message
            if time.time() - started > timeout:
                break

        return results
