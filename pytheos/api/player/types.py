#!/usr/bin/env python
""" Provides type declarations related to the PlayerAPI group """
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Lineout(Enum):
    NoLineout = 0   # FIXME: Is this correct?  Zero is not defined in the specification but my device reports as such.
    Variable = 1
    Fixed = 2

    def __str__(self):
        return str(self.value)

class Control(Enum):
    NoControl = 1
    IR = 2
    Trigger = 3
    Network = 4

    def __str__(self):
        return str(self.value)

class Network(Enum):
    Wired = 'wired'
    Wifi = 'wifi'
    Unknown = 'unknown'

    def __str__(self):
        return self.value

class RepeatMode(Enum):
    All = 'on_all'
    One = 'on_one'
    Off = 'off'

    def __str__(self):
        return self.value

class ShuffleMode(Enum):
    On = 'on'
    Off = 'off'

    def __str__(self):
        return self.value

class PlayState(Enum):
    Stopped = 'stop'
    Playing = 'play'
    Paused = 'pause'

    def __str__(self):
        return self.value

@dataclass
class PlayMode:
    repeat: RepeatMode
    shuffle: ShuffleMode

@dataclass
class QuickSelect:
    id: int
    name: str

@dataclass
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
            self.network = Network(from_dict.get('network', Network.Unknown))
            self.ip = from_dict.get('ip')
            self.lineout = Lineout(int(from_dict.get('lineout', str(Lineout.NoLineout))))
            self.serial = from_dict.get('serial')

            control = from_dict.get('control')
            if control is not None:
                control = Control(int(control))
            self.control = control

@dataclass
class MediaItem:
    """ Represents a piece of media """
    song: str
    album: str
    artist: str
    image_url: str
    queue_id: int
    media_id: str
    album_id: str

    # Special fields to support get_now_playing_media
    type: str
    source_id: str = None
    container_id: str = None

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

            self.type = from_dict.get('type')
            self.source_id = from_dict.get('sid')
            self.container_id = from_dict.get('cid')
