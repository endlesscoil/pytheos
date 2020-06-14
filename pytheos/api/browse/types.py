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

    def __str__(self):
        return str(self.value)


class SourceMediaType(Enum):
    Artist = 'artist'
    Album = 'album'
    Song = 'song'
    Container = 'container'
    Station = 'station'

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
    Analog = 'inputs/analog'

    def __str__(self):
        return str(self.value)

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

@dataclass
class SearchCriteria:
    name: str = ""
    search_criteria_id: str = ""
    wildcard: bool = False
    playable: bool = False
    container_id: str = "" # Prefix to add to search string to play directly from results.  Only valid if playable=True.

    def __init__(self, from_dict: Optional[dict]=None):
        if from_dict:
            self.name = from_dict.get('name')
            self.search_criteria_id = from_dict.get('scid')
            self.wildcard = bool(from_dict.get('wildcard', False))
            self.playable = bool(from_dict.get('playable', False))
            self.container_id = from_dict.get('cid')
