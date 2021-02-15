#!/usr/bin/env python
from __future__ import annotations

import http.client
import socket


class SSDPResponse(http.client.HTTPResponse):
    """ Specialized http.client Response object to facilitate parsing SSDP responses """

    def __init__(self, sock: socket.socket):
        super().__init__(sock)

        self.begin()
        self.location = self.getheader("location")
        self.usn = self.getheader("usn")
        self.st = self.getheader("st")
        self.cache = self.getheader("cache-control").split("=")[1]

    def __repr__(self):
        return f"<SSDPResponse(location={self.location})>"


class NewSSDPResponse:
    def __init__(self, response):
        self.headers = {}

        fields = response.split('\r\n')
        if len(fields) == 0:
            raise ValueError('Invalid SSDP Response')

        self.protocol, self.response_code, self.response = fields[0].split(' ')
        for f in fields[1:]:
            split_values = f.split(':')

            field_name = split_values[0]
            field_value = ':'.join(split_values[1:]).strip()
            if field_name == '':
                continue

            self.headers[field_name] = field_value

        self.location = self.headers.get('LOCATION')

    def __repr__(self):
        return f"<SSDPResponse(location={self.location})>"
