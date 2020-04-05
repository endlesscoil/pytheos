#!/usr/bin/env python
from __future__ import annotations

import socket

import netifaces

from .pytheos import Pytheos
from .types import SSDPResponse

DEFAULT_BROADCAST_ADDRESS = '239.255.255.250'
DEFAULT_BROADCAST_PORT = 1900
SSDP_MESSAGE_FORMAT = "\r\n".join([
    'M-SEARCH * HTTP/1.1',
    'HOST: {address}:{port}',
    'MAN: "ssdp:discover"',
    'ST: {st}',
    'MX: {mx}',
    '',
    ''
])


def discover(service, address=DEFAULT_BROADCAST_ADDRESS, port=DEFAULT_BROADCAST_PORT, timeout=5, retries=1, mx=3, bind_ip=None):
    discovered_devices = []

    socket.setdefaulttimeout(timeout)
    if not bind_ip:
        bind_ip = get_default_ip(socket.AF_INET)

    for attempt in range(retries):
        sock = _create_socket(address, bind_ip)

        message_bytes = SSDP_MESSAGE_FORMAT.format(address=address, port=port, st=service, mx=mx).encode('utf-8')
        sock.sendto(message_bytes, (address, port))

        try:
            response = SSDPResponse(sock)
            discovered_devices.append(Pytheos(None, port=port, from_response=response))

        except socket.timeout:
            break

        sock.close()

    return discovered_devices

def get_default_ip(proto):
    gateway, inf = get_default_interface(socket.AF_INET)
    return _get_interface_ip(inf, proto)

def get_default_interface(proto):
    gateways = netifaces.gateways()
    return gateways['default'].get(proto)

def _get_interface_ip(interface, proto):
    addresses = netifaces.ifaddresses(interface)
    proto_address = addresses.get(proto)
    if not proto_address:
        return None

    return proto_address[0].get('addr')

def _create_socket(broadcast_address, local_ip, so_reuseaddr=True, ttl=2):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 if so_reuseaddr else 0)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local_ip))  # Required for Windows
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    membership_request = socket.inet_aton(broadcast_address) + socket.inet_aton(local_ip)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_request)        # Required for Windows

    return sock
