#!/usr/bin/env python
import socket
import http.client

import netifaces


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
            discovered_devices.append(response)

        except socket.timeout:
            break

    return discovered_devices # FIXME: Should really be returning Pytheos instances.

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
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local_ip))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    membership_request = socket.inet_aton(broadcast_address) + socket.inet_aton(local_ip)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_request)

    return sock

class SSDPResponse(http.client.HTTPResponse):
    def __init__(self, sock):
        super().__init__(sock)

        self.begin()
        self.location = self.getheader("location")
        self.usn = self.getheader("usn")
        self.st = self.getheader("st")
        self.cache = self.getheader("cache-control").split("=")[1]

    def __repr__(self):
        return f"<SSDPResponse(location={self.location})>"
