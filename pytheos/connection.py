#!/usr/bin/env python
""" Provides the implementation for the Connection class """

from __future__ import annotations

import logging
import telnetlib
import threading
from typing import Optional

logger = logging.getLogger(__name__)


class Connection:
    """ Connection to the telnet service on a HEOS device """

    @property
    def connected(self) -> bool:
        return self._conn.get_socket() is not None if self._conn else None

    def __init__(self):
        self.server = None
        self.port = None
        self.deduplicate = None

        self._lock = threading.Lock()
        self._conn: Optional[telnetlib.Telnet] = None

    def __del__(self):
        if self._conn:
            self.close()

    def connect(self, server: str, port: int, deduplicate: bool=False):
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

            self._conn = telnetlib.Telnet(self.server, self.port)

    def close(self):
        """ Closes the connection

        :return: None
        """
        with self._lock:
            if self._conn:
                self._conn.close()
                self._conn = None

    def write(self, input: bytes):
        """ Writes the provided data to the connection

        :param input: Data to write
        :return: None
        """
        if self._conn:
            with self._lock:
                self._conn.write(input)

    def read_until(self, target: bytes, timeout: Optional[int]=None) -> bytes:
        """ Reads from the connection until the target string is found or the optional timeout is hit

        :param target: Target string
        :param timeout: Timeout (seconds) or None for no timeout
        :return: str
        """
        data = None

        if self._conn:
            with self._lock:
                data = self._conn.read_until(target, timeout=timeout)

        return data
