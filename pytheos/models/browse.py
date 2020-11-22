#!/usr/bin/env python
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


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
