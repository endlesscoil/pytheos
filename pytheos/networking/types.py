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
