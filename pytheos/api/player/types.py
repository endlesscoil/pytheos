#!/usr/bin/env python
""" Provides type declarations related to the PlayerAPI group """
from __future__ import annotations

from enum import Enum
from typing import Optional


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

class Player:
    """ Player representation """

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

    def __init__(self, from_dict: Optional[dict]=None):
        """ Constructor

        :param from_dict: Optional dictionary to use for initialization
        """
        if from_dict:
            self.name = from_dict.get('name')
            self.player_id = from_dict.get('pid')
            self.group_id = from_dict.get('gid')
            self.model = from_dict.get('model')
            self.version = from_dict.get('version')
            self.network = Network(from_dict.get('network'))
            self.ip = from_dict.get('ip')
            self.lineout = Lineout(int(from_dict.get('lineout')))
            self.serial = from_dict.get('serial')

            control = from_dict.get('control')
            if control is not None:
                control = Control(int(control))
            self.control = control


class QueueItem:
    """ Represents an item in the play queue """
    song: str
    album: str
    artist: str
    image_url: str
    queue_id: int
    media_id: int
    album_id: int

    def __init__(self, from_dict: Optional[dict]=None):
        """ Constructor

        :param from_dict: Optional dictionary to use for initialization
        """
        if from_dict:
            self.song = from_dict.get('song')
            self.album = from_dict.get('album')
            self.artist = from_dict.get('artist')
            self.image_url = from_dict.get('image_url')
            self.queue_id = from_dict.get('qid')
            self.media_id = from_dict.get('mid')
            self.album_id = from_dict.get('album_id')
