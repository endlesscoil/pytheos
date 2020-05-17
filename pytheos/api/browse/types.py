#!/usr/bin/env python
from dataclasses import dataclass
from enum import Enum


class SourceType(Enum):
    MusicService = 'music_service'
    HeosService = 'heos_service'
    HeosServer = 'heos_server'
    DLNAServer = 'dlna_server'


@dataclass
class MusicSource:
    name: str = None
    image_url: str = None
    type: SourceType = None
    source_id: int = None
    available: bool = False
    service_username: str = None
