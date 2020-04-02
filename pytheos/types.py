#!/usr/bin/env python
import http.client
import json


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

    def __init__(self, from_json=None):
        if from_json:
            self.command = from_json.get('command')
            self.result = from_json.get('result')
            self.message = from_json.get('message')

    def __str__(self):
        return f'{self.command} - {self.result} - {self.message}'

    def __repr__(self):
        return f'<HEOSResult(command={self.command}, result={self.result}, message={self.message})>'


class HEOSEvent(object):
    group: str = None
    command: str = None
    message: str = None
    raw_string: str = None

    def __init__(self, from_json=None):
        if from_json:
            heos = from_json.get('heos', {})

            self.group, self.command = heos.get('command').split('/')
            self.message = heos.get('message')
            self.raw_string = json.dumps(from_json)

            if self.message:
                vars = {
                    k: v.strip("'") for k, v in dict(
                        [var_string.split('=') for var_string in self.message.split('&')]
                    ).items()
                }

                for name, value in vars.items():
                    setattr(self, name, value)

    def __str__(self):
        return self.raw_string

    def __repr__(self):
        return f'<HEOSEvent(group="{self.group}", command="{self.command}", message="{self.message}")>'
