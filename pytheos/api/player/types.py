#!/usr/bin/env python
from dataclasses import dataclass
from enum import Enum


class Lineout(Enum):
    NoLineout = 0   # FIXME: Correct?
    Variable = 1
    Fixed = 2

class Control(Enum):
    NoControl = 1
    IR = 2
    Trigger = 3
    Network = 4

class Network(Enum):
    Wired = 'wired'
    Wifi = 'wifi'
    Unknown = 'unknown'

@dataclass
class Player(object):
    name: str
    player_id: str
    group_id: str
    model: str
    version: str
    network: Network
    ip: str
    lineout: Lineout
    control: Control
    serial: str

    def __init__(self, from_dict=None):
        if from_dict:
            self.name = from_dict.get('name')
            self.player_id = from_dict.get('pid')
            self.group_id = from_dict.get('gid')
            self.model = from_dict.get('model')
            self.version = from_dict.get('version')
            self.network = Network(from_dict.get('network'))
            self.ip = from_dict.get('ip')
            self.lineout = Lineout(int(from_dict.get('lineout')))

            control = from_dict.get('control')
            if control is not None:
                control = Control(int(control))
            self.control = control

            self.serial = from_dict.get('serial')
