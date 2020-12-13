#!/usr/bin/env python
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


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


@dataclass
class Source:
    name: str = None
    type: SourceType = None
    available: bool = False
    playable: bool = False
    container: bool = False

    source_id: int = None
    container_id: int = None
    media_id: int = None

    image_url: str = None
    service_username: str = None

    def __init__(self, from_dict: Optional[dict]=None, parent_source_id=None, parent_container_id=None):
        """ Constructor

        :param from_dict: Optional dictionary to use for initialization
        """
        if from_dict:
            self.name = from_dict.get('name')
            self.type = SourceType(from_dict.get('type'))
            self.available = from_dict.get('available')
            self.playable = from_dict.get('playable')
            self.container = bool(from_dict.get('container'))
            self.source_id = from_dict.get('sid')
            self.container_id = from_dict.get('cid')
            self.media_id = from_dict.get('mid')
            self.image_url = from_dict.get('image_url')
            self.service_username = from_dict.get('service_username')

        if not self.source_id:
            self.source_id = parent_source_id

        if not self.container_id:
            self.container_id = parent_container_id
