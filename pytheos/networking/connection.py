#!/usr/bin/env python
""" Provides the implementation for the Connection class """

from __future__ import annotations

import json
import logging
import threading
import time
from typing import Optional, Union
import asyncio

from .. import utils
from ..api import BrowseAPI, GroupAPI, PlayerAPI, SystemAPI
from ..networking.errors import CommandFailedError
from ..models.heos import HEOSResult

logger = logging.getLogger(__name__)


class Connection:
    """ Connection to the telnet service on a HEOS device """

    CONNECTION_READ_TIMEOUT = 1
    MESSAGE_READ_TIMEOUT = 1        # FIXME: I suspect that this needs to be larger.
    DELAY_MESSAGES = (
        "command under process",
        "processing previous command"
    )

    @property
    def connected(self) -> bool:
        return self._conn.get_socket() is not None if self._conn else None

    @property
    def prettify_json_response(self):
        return self._prettify_json_response

    @prettify_json_response.setter
    def prettify_json_response(self, value):
        self._prettify_json_response = value
        self.system.prettify_json_response(value)

    def __init__(self):
        self.server = None
        self.port = None
        self.deduplicate = None

        self.system = SystemAPI(self)
        self.player = PlayerAPI(self)
        self.group = GroupAPI(self)
        self.browse = BrowseAPI(self)

        self._prettify_json_response = False
        self._lock = threading.Lock()
        #self._conn: Optional[telnetlib.Telnet] = None
        self._reader = None
        self._writer = None
        self._last_response: Optional[str] = None

    def __del__(self):
        # if self._reader:
        #     self._reader.close()
        # if self._writer:
        #     self._writer.close()
        pass

    async def connect(self, server: str, port: int, deduplicate: bool=False):
        """ Establish a connection with the HEOS service

        :param server: Server hostname or IP
        :param port: Port number
        :param deduplicate: Flag to enable message deduplication
        :return: None
        """
        with self._lock:
            self.server = server
            self.port = port
            self.deduplicate = deduplicate

            self._reader, self._writer = await asyncio.open_connection(server, port)

    def close(self):
        """ Closes the connection

        :return: None
        """
        with self._lock:
            if self._reader:
                self._reader.close()
                self._reader = None

            if self._writer:
                self._writer.close()
                self._writer = None

    def write(self, input_data: bytes):
        """ Writes the provided data to the connection

        :param input_data: Data to write
        :return: None
        """
        if self._writer:
            with self._lock:
                self._writer.write(input_data)

    async def read_until(self, target: bytes, timeout: Optional[int]=None) -> bytes:
        """ Reads from the connection until the target string is found or the optional timeout is hit

        :param target: Target string
        :param timeout: Timeout (seconds) or None for no timeout
        :return: str
        """
        data = None

        if self._reader:
            with self._lock:
                data = await self._reader.readuntil(target)

        return data

    async def call(self, group: str, command: str, **kwargs: dict) -> HEOSResult:
        """ Formats a HEOS API request, submits it, and reads the response.

        :param group: Group name (e.g. system, player, etc)
        :param command: Command name (e.g. heart_beat)
        :param kwargs: Any parameters that should be sent along with the command
        :raises: AssertionError, CommandFailedError
        :return: HEOSResult
        """
        self.send_command(group, command, **kwargs)
        message = await self.read_message()
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
        self.write(command_string.encode('utf-8'))
        logger.debug(f"Sending command: {command_string.rstrip()}")

    async def read_message(self, timeout: int=MESSAGE_READ_TIMEOUT, delimiter: bytes=b'\r\n') -> Optional[dict]:
        """ Reads a message from the connection

        :param timeout: Timeout (seconds)
        :param delimiter: Message delimiter
        :return: bytes
        """
        results = None
        response = b''

        started = time.time()
        while True:
            response += await self.read_until(delimiter, timeout=self.CONNECTION_READ_TIMEOUT)

            if delimiter in response:
                response = response.strip()
                logger.debug(f"Got response: {response}")

                # Bail out if we got a duplicate message and have deduplicate enabled
                if self.deduplicate and response == self._last_response:
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

    async def heart_beat(self):
        """ Performs a system/heart_beat API call on the connection in order to keep the connection alive.

        :return: None
        """
        await self.system.heart_beat()
