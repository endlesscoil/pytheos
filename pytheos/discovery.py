#!/usr/bin/env python
""" This module provides the discovery functionality for Pytheos """

from __future__ import annotations

import logging
import socket
from typing import Optional, List

from . import utils
from .pytheos import Pytheos
from .types import SSDPResponse

logger = logging.getLogger(__name__)


def discover(timeout: Optional[int]=None, retries: Optional[int]=None, mx: Optional[int]=None) -> List[Pytheos]:
    """ Convenience function for initiating the discovery process.

    :param timeout: Optional override for the default timeout
    :param retries: Optional override for the default number of retries
    :param mx: Optional override for the default MX value
    :return: list
    """
    discovery = Discovery()
    devices = discovery.discover(timeout, retries, mx)

    return devices


class SSDPBroadcastMessage:
    """ Representation of an SSDP message """

    def __init__(self, address: str, port: int, service: str, mx: int):
        """ Constructor

        :param address: Broadcast address
        :param port: Broadcast port
        :param service: SSDP service
        :param mx: MX value
        """
        self.address = address
        self.port = port
        self.service = service
        self.mx = mx

    def __str__(self):
        return "\r\n".join([
            'M-SEARCH * HTTP/1.1',
            f'HOST: {self.address}:{self.port}',
            'MAN: "ssdp:discover"',
            f'ST: {self.service}',
            f'MX: {self.mx}',
            '',
            ''
        ])


class Discovery:
    """ HEOS discovery implementation """
    DEFAULT_BROADCAST_ADDRESS = '239.255.255.250'
    DEFAULT_BROADCAST_PORT = 1900
    DEFAULT_BIND_PORT = 12112
    DEFAULT_TTL = 3
    DEFAULT_SERVICE = "urn:schemas-denon-com:device:ACT-Denon:1"
    DEFAULT_TIMEOUT = 5
    DEFAULT_RETRIES = 1
    DEFAULT_MX = 3

    def __init__(self,
                 broadcast_address: Optional[str]=DEFAULT_BROADCAST_ADDRESS,
                 broadcast_port: Optional[int]=DEFAULT_BROADCAST_PORT,
                 bind_ip: Optional[str]=None):
        """ Constructor

        :param broadcast_address: Broadcast address to use
        :param broadcast_port: Broadcast port to use
        :param bind_ip: Optional IP address to bind to - use None for first interface
        """
        self.service = self.DEFAULT_SERVICE
        self.address = broadcast_address
        self.port = broadcast_port
        self.timeout = self.DEFAULT_TIMEOUT
        self.retries = self.DEFAULT_RETRIES
        self.mx = self.DEFAULT_MX
        self.bind_ip = bind_ip
        self.bind_port = self.DEFAULT_BIND_PORT
        self.ttl = self.DEFAULT_TTL
        self.reuse_addr = True

        self._socket = None

    def discover(self, timeout: int=None, retries: int=None, mx: int=None) -> List[Pytheos]:
        """ Performs SSDP broadcasts to identify any HEOS devices on the network

        :param timeout: Timeout (seconds)
        :param retries: Number of retries
        :param mx: MX value
        :return: list
        """
        socket.setdefaulttimeout(timeout if timeout is not None else self.timeout)
        if not self.bind_ip:
            self.bind_ip = utils.get_default_ip(socket.AF_INET)

        return self._perform_discovery(retries, mx)

    def _perform_discovery(self, retries: Optional[int]=None, mx: Optional[int]=None) -> List[Pytheos]:
        """ Performs the discovery process.

        :param retries: Optional override for the number of retries
        :param mx: Optional override for the MX value
        :return: list
        """
        logger.debug(f"Binding to IP: {self.bind_ip}")

        retries = retries if retries is not None else self.retries
        mx = mx if mx is not None else self.mx

        discovered_devices = []
        for attempt in range(retries):
            logger.debug(f"Broadcasting discovery to {self.address}:{self.port}")

            devices = self._communicate(mx)
            if not devices:
                continue

            logger.info(f"Discovered {len(devices)} new devices..")
            discovered_devices.extend(devices)

        return discovered_devices

    def _communicate(self, mx: int) -> List[Pytheos]:
        """ Create our socket, construct the broadcast message, send it, and read the responses.

        :param mx: MX value to use
        :return: list
        """
        self._socket = self._create_socket()

        msg = self._build_message(mx)
        self._send_message(msg)

        devices = []
        while True:
            device = self._handle_response()
            if not device:
                break

            devices.append(device)

        self._close_socket()

        return devices

    def _handle_response(self):
        """ Reads a response to the SSDP broadcast.

        :return: Pytheos device
        """
        device = None

        try:
            response = self._read_response()
            device = Pytheos(from_response=response)

        except socket.timeout:
            pass

        return device

    def _read_response(self):
        return SSDPResponse(self._socket)

    def _build_message(self, mx: int) -> bytes:
        """ Constructs the broadcast message to send.

        :param mx: MX value
        :return: bytes
        """
        broadcast_message = SSDPBroadcastMessage(self.address, self.port, self.service, mx)
        return str(broadcast_message).encode('utf-8')

    def _send_message(self, message: bytes):
        """ Sends the message to the socket.

        :param message: Message
        :return: None
        """
        logger.debug(f'Sending message {message}')
        self._socket.sendto(message, (self.address, self.port))

    def _create_socket(self):
        """ Create the socket we will use to broadcast our SSDP request.

        :return: socket
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, int(self.reuse_addr))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.bind_ip))  # Required for Windows
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ttl)

        membership_request = socket.inet_aton(self.address) + socket.inet_aton(self.bind_ip)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_request)            # Required for Windows
        sock.bind((self.bind_ip, self.bind_port))

        return sock

    def _close_socket(self):
        """ Close the socket """
        self._socket.close()
        self._socket = None
