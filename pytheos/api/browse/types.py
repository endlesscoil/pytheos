#!/usr/bin/env python
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SourceType(Enum):
    MusicService = 'music_service'
    HeosService = 'heos_service'
    HeosServer = 'heos_server'
    DLNAServer = 'dlna_server'

    Artist = 'artist' # HACK: WTF?


class SourceMediaType(Enum):
    Artist = 'artist'
    Album = 'album'
    Song = 'song'
    Container = 'container'
    Station = 'station'


@dataclass
class MusicSource:
    name: str = None
    image_url: str = None
    type: SourceType = None
    source_id: int = None
    available: bool = False
    service_username: str = None

    def __init__(self, from_dict: Optional[dict]=None):
        """ Constructor

        :param from_dict: Optional dictionary to use for initialization
        """
        if from_dict:
            self.name = from_dict.get('name')
            self.image_url = from_dict.get('image_url')
            self.type = SourceType(from_dict.get('type'))
            self.source_id = from_dict.get('sid')
            self.available = from_dict.get('available')
            self.service_username = from_dict.get('service_username')


@dataclass
class SourceMedia:
    container: bool = False
    playable: bool = False
    type: SourceMediaType = None
    name: str = None
    image_url: str = None
    source_id: int = None
    container_id: int = None
    media_id: int = None

    def __init__(self, from_dict: Optional[dict]=None):
        """ Constructor

        :param from_dict: Optional dictionary to use for initialization
        """
        if from_dict:
            self.container = from_dict.get('container')
            self.playable = from_dict.get('playable')
            self.type = from_dict.get('type') # FIXME SourceMediaType()
            self.name = from_dict.get('name')
            self.image_url = from_dict.get('image_url')
            self.source_id = from_dict.get('sid')
            self.container_id = from_dict.get('cid')
            self.media_id = from_dict.get('mid')
