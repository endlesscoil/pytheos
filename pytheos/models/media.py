#!/usr/bin/env python
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


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

    @property
    def name(self):
        return f"{self.artist} - {self.song}"

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
