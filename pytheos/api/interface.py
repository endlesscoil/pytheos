#!/usr/bin/env python
""" Provides the APIInterface implementation """

from __future__ import annotations

import json
import time
import logging
from typing import Optional, Union

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

    CONNECTION_READ_TIMEOUT = 1
    MESSAGE_READ_TIMEOUT = 1        # FIXME: I suspect that this needs to be larger.
    DELAY_MESSAGES = (
        "command under process",
        "processing previous command"
    )

    def __init__(self, connection):
        self.system = SystemAPI(self)
        self.player = PlayerAPI(self)
        self.group = GroupAPI(self)
        self.browse = BrowseAPI(self)

        self._connection = connection
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
            #if results.header.result is None:
            #    raise CommandFailedError('No "result" found in "heos" response', results)

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

    def read_message(self, timeout: int=MESSAGE_READ_TIMEOUT, delimiter: bytes=b'\r\n') -> Optional[dict]:
        """ Reads a message from the connection

        :param timeout: Timeout (seconds)
        :param delimiter: Message delimiter
        :return: bytes
        """
        results = None
        response = b''

        started = time.time()
        while True:
            response += self._connection.read_until(delimiter, timeout=self.CONNECTION_READ_TIMEOUT)

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
                    response = b''  # Not valid JSON; reset & retry
                    continue

                if self._results_are_delayed(results['heos'].get('message', '')):
                    logger.debug("Delayed - command under process")
                    response = b''
                    continue

                # Valid data
                break

            # And break out if we exceeded our time limit to read a valid message.  We are also considering delayed
            # responses as valid in terms of timeout.
            if time.time() - started > timeout and not self._results_are_delayed(self._last_response):
                break

        return results

    def _results_are_delayed(self, message: Union[str, bytes]) -> bool:
        """ Checks for a message matching known messages that indicate there is a delay in processing
        results.

        :param message: Message string
        :return: bool
        """
        if not message:
            return False

        if isinstance(message, bytes):
            message = message.decode('utf-8', 'ignore')

        return any([msg.lower() in message.lower() for msg in self.DELAY_MESSAGES])
