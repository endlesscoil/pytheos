#!/usr/bin/env python
""" Provides the implementation for the Connection class """

from __future__ import annotations

import telnetlib
import threading
from typing import Optional

from .api.container import APIContainer


class Connection:
    """ Connection to the telnet service on a HEOS device """

    def __init__(self, server: str, port: int, deduplicate: bool=False):
        """ Constructor

        :param server: Server hostname or IP
        :param port: Port number
        :param deduplicate: Flag to enable message deduplication
        """
        self.server = server
        self.port = port
        self.deduplicate = deduplicate
        self.api = APIContainer(self)

        self._lock = threading.Lock()
        self._conn: Optional[telnetlib.Telnet] = None

    def __del__(self):
        if self._conn:
            self.close()

    @property
    def connected(self) -> bool:
        return self._conn.get_socket() is not None if self._conn else None

    def connect(self) -> None:
        """ Establish a connection with the HEOS service

        :return: None
        """
        with self._lock:
            self._conn = telnetlib.Telnet(self.server, self.port)

    def close(self) -> None:
        """ Closes the connection

        :return: None
        """
        with self._lock:
            self._conn.close()
            self._conn = None

    def write(self, input: bytes) -> None:
        """ Writes the provided data to the connection

        :param input: Data to write
        :return: None
        """
        with self._lock:
            self._conn.write(input)

    def read_until(self, target: bytes, timeout: Optional[int]=None) -> bytes:
        """ Reads from the connection until the target string is found or the optional timeout is hit

        :param target: Target string
        :param timeout: Timeout (seconds) or None for no timeout
        :return: str
        """
        with self._lock:
            data = self._conn.read_until(target, timeout=timeout)

        return data

    def register_for_events(self, enable: bool=True) -> None:
        """ Registers this connection to receive change events

        :param enable: True or False
        :return: None
        """
        self.api.system.register_for_change_events(enable)
