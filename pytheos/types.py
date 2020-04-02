#!/usr/bin/env python
import http.client
from dataclasses import dataclass


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


@dataclass
class HEOSResult(object):
    command: str = None
    result: str = None
    message: str = None

    @property
    def succeeded(self):
        return self.result and self.result.lower() == 'success'

    def __init__(self, from_json=None):
        if from_json:
            self.command = from_json.get('command')
            self.result = from_json.get('result')
            self.message = from_json.get('message')

    def __str__(self):
        return f'{self.command} - {self.result} - {self.message}'

    def __repr__(self):
        return f'<HEOSResult(command={self.command}, result={self.result}, message={self.message})>'
