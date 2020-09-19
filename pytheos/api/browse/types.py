#!/usr/bin/env python
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SourceType(Enum):
    # Service types
    MusicService = 'music_service'
    HeosService = 'heos_service'
    HeosServer = 'heos_server'
    DLNAServer = 'dlna_server'

    # Media types
    Artist = 'artist'
    Album = 'album'
    Song = 'song'
    Container = 'container'
    Station = 'station'
    Playlist = 'playlist'

    @property
    def is_container(self):
        return self in [
            SourceType.Album,
            SourceType.Container,
            SourceType.Station,
            SourceType.Playlist
        ]

    def __str__(self):
        return str(self.value)


class InputSource(Enum):
    AuxIn1 = 'inputs/aux_in_1'
    AuxIn2 = 'inputs/aux_in_2'
    AuxIn3 = 'inputs/aux_in_3'
    AuxIn4 = 'inputs/aux_in_4'
    AuxSingle = 'inputs/aux_single'
    Aux1 = 'inputs/aux1'
    Aux2 = 'inputs/aux2'
    Aux3 = 'inputs/aux3'
    Aux4 = 'inputs/aux4'
    Aux5 = 'inputs/aux5'
    Aux6 = 'inputs/aux6'
    Aux7 = 'inputs/aux7'
    LineIn1 = 'inputs/line_in_1'
    LineIn2 = 'inputs/line_in_2'
    LineIn3 = 'inputs/line_in_3'
    LineIn4 = 'inputs/line_in_4'
    CoaxIn1 = 'inputs/coax_in_1'
    CoaxIn2 = 'inputs/coax_in_2'
    OpticalIn1 = 'inputs/optical_in_1'
    OpticalIn2 = 'inputs/optical_in_2'
    HdmiIn1 = 'inputs/hdmi_in_1'
    HdmiIn2 = 'inputs/hdmi_in_2'
    HdmiIn3 = 'inputs/hdmi_in_3'
    HdmiIn4 = 'inputs/hdmi_in_4'
    HdmiArc1 = 'inputs/hdmi_arc_1'
    CableSat = 'inputs/cable_sat'
    Dvd = 'inputs/dvd'
    Bluray = 'inputs/bluray'
    Game = 'inputs/game'
    MediaPlayer = 'inputs/mediaplayer'
    Cd = 'inputs/cd'
    Tuner = 'inputs/tuner'
    HdRadio = 'inputs/hdradio'
    TvAudio = 'inputs/tvaudio'
    Phono = 'inputs/phono'
    UsbDac = 'inputs/usbdac'
    AnalogIn1 = 'inputs/analog_in_1'
    AnalogIn2 = 'inputs/analog_in_2'
    RecorderIn1 = 'inputs/record_in_1'

    def __str__(self):
        return str(self.value)


class AddToQueueType(Enum):
    PlayNow = 1
    PlayNext = 2
    AddToEnd = 3
    ReplaceAndPlay = 4

    def __str__(self):
        return str(self.value)


class ServiceOption(Enum):
    AddTrackToLibrary = 1
    AddAlbumToLibrary = 2
    AddStationToLibrary = 3
    AddPlaylistToLibrary = 4
    RemoveTrackFromLibrary = 5
    RemoveAlbumFromLibrary = 6
    RemoveStationFromLibrary = 7
    RemovePlaylistFromLibrary = 8

    ThumbsUp = 11
    ThumbsDown = 12
    CreateNewStation = 13

    AddToFavorites = 19
    RemoveFromFavorites = 20

    def __str__(self):
        return str(self.value)


@dataclass
class Source:
    name: str = None
    type: SourceType = None
    source_id: int = None
    container: bool = False
    container_id: int = None
    image_url: str = None

    def __init__(self, from_dict: Optional[dict]=None):
        """ Constructor

        :param from_dict: Optional dictionary to use for initialization
        """
        if from_dict:
            self.name = from_dict.get('name')
            self.type = SourceType(from_dict.get('type'))
            self.image_url = from_dict.get('image_url')
            self.source_id = from_dict.get('sid')
            self.container = bool(from_dict.get('container'))
            self.container_id = from_dict.get('cid')


@dataclass
class MusicSource(Source):
    available: bool = False
    service_username: str = None

    def __init__(self, from_dict: Optional[dict]=None):
        """ Constructor

        :param from_dict: Optional dictionary to use for initialization
        """
        super().__init__(from_dict)

        if from_dict:
            self.available = from_dict.get('available')
            self.service_username = from_dict.get('service_username')


@dataclass
class SourceMedia(Source):
    playable: bool = False
    media_id: int = None
    queue_id: int = None

    def __init__(self, from_dict: Optional[dict]=None):
        """ Constructor

        :param from_dict: Optional dictionary to use for initialization
        """
        super().__init__(from_dict)

        if from_dict:
            self.container = bool(from_dict.get('container'))
            self.playable = from_dict.get('playable')
            self.type = SourceType(from_dict.get('type'))
            self.name = from_dict.get('name')
            self.image_url = from_dict.get('image_url')
            self.source_id = from_dict.get('sid')
            self.container_id = from_dict.get('cid')
            self.media_id = from_dict.get('mid')


@dataclass
class SearchCriteria:
    name: str = ""
    search_criteria_id: str = ""
    wildcard: bool = False
    playable: bool = False
    container_id: str = ""  # Prefix to add to search string to play directly from results.  Only valid if playable=True.

    def __init__(self, from_dict: Optional[dict]=None):
        if from_dict:
            self.name = from_dict.get('name')
            self.search_criteria_id = from_dict.get('scid')
            self.wildcard = bool(from_dict.get('wildcard', False))
            self.playable = bool(from_dict.get('playable', False))
            self.container_id = from_dict.get('cid')


@dataclass
class AlbumMetadata:
    album_id: str
    images: list

    def __init__(self, from_dict=None):
        self.images = []
        if from_dict:
            self.album_id = from_dict.get('album_id')
            self.images = [AlbumImage(image_data) for image_data in from_dict.get('images', [])]


@dataclass
class AlbumImage:
    image_url: str
    width: int

    def __init__(self, from_dict=None):
        if from_dict:
            self.image_url = from_dict.get('image_url')
            self.width = int(from_dict.get('width'))
