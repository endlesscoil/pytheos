#!/usr/bin/env python
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional, Union

from pytheos import utils


@dataclass
class HEOSEvent:
    """ Represents a message received from the event channel that signifies a new event has occurred. """

    vars: dict
    command: Optional[str] = None
    message: Optional[str] = None
    raw: Optional[str] = None

    def __init__(self, from_dict: dict=None):
        if from_dict:
            heos = from_dict.get('heos', {})

            self.command = heos.get('command')
            self.message = heos.get('message')
            self.raw = json.dumps(from_dict)

            # Bind any message variables to our self as attributes
            self.vars = {}
            if self.message:
                self.vars = utils.parse_var_string(self.message)

    def __str__(self):
        return self.raw

    def __repr__(self):
        return f'<HEOSEvent(command="{self.command}", message="{self.message}")>'


class HEOSHeader:
    """ Representation of the 'heos' block returned from HEOS command execution """

    command: Optional[str] = None     # HEOS Command (e.g. system/heart_beat)
    result: Optional[str] = None      # 'success' or 'fail'
    message: Optional[str] = None     # URL-ish parameter string with additional details

    def __init__(self, from_dict=None):
        self.command = from_dict.get('command')
        self.result = from_dict.get('result')
        self.message = from_dict.get('message')

        self.vars = {}
        if self.message:    # Extract variables from the message string for ease-of-access
            self.vars = utils.parse_var_string(self.message)

    def __repr__(self):
        return f'<HEOSHeader(command={self.command}, result={self.result}, message={self.message})>'


class HEOSPayload(object):
    """ Base class for the payloads returned by some HEOS command execution """

    data: Optional[dict] = None

    def __init__(self, source: Union[dict, list]=None):
        self.data = source
        self.vars = {}

        if source and isinstance(source, dict):
            message = source.get('message')
            if message:
                self.vars = utils.parse_var_string(message)


class HEOSListPayloadIterator(object):
    """ Iterator for the HEOSListPayload class """

    def __init__(self, payload):
        self._payload = payload
        self._current_index = 0

    def __next__(self):
        if not self._payload.data or self._current_index >= len(self._payload.data):
            raise StopIteration()

        result = self._payload.data[self._current_index]
        self._current_index += 1
        return result


class HEOSListPayload(HEOSPayload):
    """ Represents a list that is returned from some HEOS command execution """

    data: list

    def __iter__(self):
        return HEOSListPayloadIterator(self)


class HEOSDictPayload(HEOSPayload):
    """ Represents a dict that is returned from some HEOS command execution """

    def __init__(self, from_dict=None):
        super().__init__(source=from_dict)

    def get(self, name, default=None):
        if self.data:
            return self.data.get(name, default)

        return None


class HEOSResult(object):
    """ Represents the result of executing a HEOS command """

    header: Optional[HEOSHeader]
    payload: Optional[HEOSPayload]

    @staticmethod
    def create_payload(payload_data) -> HEOSPayload:
        """ Factory for creating the proper payload type based on the data object passed """
        if isinstance(payload_data, dict):
            payload = HEOSDictPayload(payload_data)
        elif isinstance(payload_data, list):
            payload = HEOSListPayload(payload_data)
        else:
            payload = HEOSPayload(payload_data)

        return payload

    @property
    def succeeded(self) -> bool:
        return self.header.result and self.header.result.lower() == 'success'

    def __init__(self, from_dict=None):
        self.header = None
        self.payload = None
        if from_dict:
            heos = from_dict.get('heos')
            if not heos:
                raise ValueError('No "heos" block found in response.')

            self.header = HEOSHeader(heos)
            self.payload = HEOSResult.create_payload(from_dict.get('payload'))

    def __repr__(self):
        return f'<HEOSResult(command={self.header!r})>'
