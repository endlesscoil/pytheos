#!/usr/bin/env python
""" This module provides the discovery functionality for Pytheos """

from __future__ import annotations

import logging
import socket
import asyncio
from asyncio import transports
from typing import Optional, List

from .. import utils
from ..networking.types import SSDPResponse, SSDPResponse

logger = logging.getLogger(__name__)


async def discover(timeout: int) -> List[SSDPResponse]:
    """ Convenience function for initiating the discovery process.

    :param timeout: Optional override for the default timeout
    :return: list
    """
    loop = asyncio.get_running_loop()
    discovery = Discovery()

    return [SSDPResponse(itm) for itm in await loop.create_task(discovery.discover(timeout))]


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


class SSDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, address, bind_ip, bind_port, reuse_addr, ttl):
        super().__init__()

        self.transport = None
        self.address = address
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.reuse_addr = reuse_addr
        self.ttl = ttl

        self.results = []

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.transport = transport

        sock = self.transport.get_extra_info('socket')
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, int(self.reuse_addr))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.bind_ip))  # Required for Windows
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ttl)

        membership_request = socket.inet_aton(self.address) + socket.inet_aton(self.bind_ip)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_request)            # Required for Windows

    def datagram_received(self, data, addr):
        self.results.append(data.decode())

    async def get_results(self):
        for r in self.results:
            yield r


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
        self.results = []
        self._socket = None

    async def send_broadcast(self, transport):
        broadcast_message = SSDPBroadcastMessage(
            self.address,
            self.port,
            self.service,
            self.mx
        )

        sock = transport.get_extra_info('socket')
        msg = str(broadcast_message).encode('utf-8')
        sock.sendto(msg, (self.address, self.port))

    async def discover(self, timeout):
        self.results = []

        loop = asyncio.get_running_loop()
        local_ip = utils.get_default_ip(socket.AF_INET)
        proto = SSDPProtocol(
            self.address,
            local_ip,
            self.bind_port,
            reuse_addr=self.reuse_addr,
            ttl=self.ttl
        )

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: proto,
            local_addr=(local_ip, self.bind_port)
        )

        try:
            await self.send_broadcast(transport)
            await asyncio.sleep(timeout)
            self.results = [itm async for itm in proto.get_results()]

        finally:
            transport.close()

        return self.results
