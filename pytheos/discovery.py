#!/usr/bin/env python
""" This module provides the discovery functionality for Pytheos """
# FIXME: Convert this whole thing to a static class.

from __future__ import annotations

import logging
import socket
from typing import Optional, List

import netifaces

from .pytheos import Pytheos
from .types import SSDPResponse

logger = logging.getLogger(__name__)


DEFAULT_BROADCAST_ADDRESS = '239.255.255.250'
DEFAULT_BROADCAST_PORT = 1900

# FIXME: Convert this into a class
SSDP_MESSAGE_FORMAT = "\r\n".join([
    'M-SEARCH * HTTP/1.1',
    'HOST: {address}:{port}',
    'MAN: "ssdp:discover"',
    'ST: {st}',
    'MX: {mx}',
    '',
    ''
])


def discover(service: str="urn:schemas-denon-com:device:ACT-Denon:1",
             address: str=DEFAULT_BROADCAST_ADDRESS,
             port: int=DEFAULT_BROADCAST_PORT,
             timeout: int=5,
             retries: int=1,
             mx :int=3,
             bind_ip: Optional[str]=None) -> List[Pytheos]:
    """ Performs SSDP broadcasts to identify any HEOS devices on the network

    :param service: Service URN to broadcast for
    :param address: Broadcast address to use
    :param port: Broadcast port to use
    :param timeout: Timeout (seconds)
    :param retries: Number of retries
    :param mx: MX value
    :param bind_ip: Optional IP address to bind to.  Default interface is used if unspecified.
    :return: list
    """
    discovered_devices = []

    socket.setdefaulttimeout(timeout)
    if not bind_ip:
        bind_ip = get_default_ip(socket.AF_INET)

    logger.debug(f"Broadcasting discovery to {address}:{port}")
    logger.debug(f"Binding to IP: {bind_ip}")

    for attempt in range(retries):
        sock = _create_socket(address, bind_ip)

        message_bytes = SSDP_MESSAGE_FORMAT.format(address=address, port=port, st=service, mx=mx).encode('utf-8')
        logger.debug(f'Sending message {message_bytes}')

        sock.sendto(message_bytes, (address, port))
        #ba = bytearray()
        #sock.recv_into(ba)
        #import pdb; pdb.set_trace()

        try:
            response = SSDPResponse(sock)
            device = Pytheos(None, port=1255, from_response=response) # FIXME: port

            logger.info(f"Discovered new device: {device}")

            discovered_devices.append(device)

        except socket.timeout as ex:
            print(f'wtf: {ex}')
            break

        sock.close()

    return discovered_devices

def get_default_ip(address_family: socket.AddressFamily) -> str:
    """ Retrieves the IP address on the default interface

    :param address_family: Address family
    :return: str
    """
    gateway, inf = get_default_interface(address_family)
    return _get_interface_ip(inf, address_family)

def get_default_interface(address_family: socket.AddressFamily) -> tuple:
    """ Retrieves the default gateway and interface for the specified address family.

    :param address_family: Address family
    :return: tuple
    """
    gateways = netifaces.gateways()
    return gateways['default'].get(address_family)

def _get_interface_ip(interface: str, address_family: socket.AddressFamily) -> Optional[str]:
    """ Retrieves the IP address of the specified interface.

    :param interface: Interface name
    :param address_family: Address family
    :return: str or None if not found
    """
    addresses = netifaces.ifaddresses(interface)
    proto_address = addresses.get(address_family)
    if not proto_address:
        return None

    return proto_address[0].get('addr')

def _create_socket(broadcast_address: str, local_ip: str, so_reuseaddr: bool=True, ttl: int=5):
    """

    :param broadcast_address: Broadcast address to use
    :param local_ip: Local IP to bind to
    :param so_reuseaddr: Flag to enable SO_REUSEADDR
    :param ttl: TTL
    :return: socket
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 if so_reuseaddr else 0)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local_ip))  # Required for Windows
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    membership_request = socket.inet_aton(broadcast_address) + socket.inet_aton(local_ip)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_request)        # Required for Windows
    sock.bind((local_ip, 12112))

    return sock
