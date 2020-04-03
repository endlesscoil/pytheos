#!/usr/bin/env python
import http.client
import json

from pytheos import utils


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


class HEOSResult(object):
    command: str = None
    result: str = None
    message: str = None

    @property
    def succeeded(self):
        return self.result and self.result.lower() == 'success'

    def __init__(self, from_dict=None):
        if from_dict:
            self.command = from_dict.get('command')
            self.result = from_dict.get('result')
            self.message = from_dict.get('message')

    def __str__(self):
        return f'{self.command} - {self.result} - {self.message}'

    def __repr__(self):
        return f'<HEOSResult(command={self.command}, result={self.result}, message={self.message})>'


class HEOSEvent(object):
    command: str = None
    message: str = None
    raw: str = None

    def __init__(self, from_dict=None):
        if from_dict:
            heos = from_dict.get('heos', {})

            self.command = heos.get('command')
            self.message = heos.get('message')
            self.raw = json.dumps(from_dict)

            if self.message:
                vars = utils.parse_var_string(self.message)

                for name, value in vars.items():
                    setattr(self, name, value)

    def __str__(self):
        return self.raw

    def __repr__(self):
        return f'<HEOSEvent(command="{self.command}", message="{self.message}")>'
