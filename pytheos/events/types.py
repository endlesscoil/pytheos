#!/usr/bin/env python
import json
from dataclasses import dataclass
from typing import Optional

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
