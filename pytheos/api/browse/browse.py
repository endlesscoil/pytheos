#!/usr/bin/env python
from typing import Optional

from pytheos.api.api import API
from pytheos.api.browse.types import MusicSource


class BrowseAPI(API):
    def get_music_sources(self) -> list:
        results = self._pytheos.api.call('browse', 'get_music_sources')
        return [MusicSource(source) for source in results.payload]

    def get_source_info(self, source_id: int) -> Optional[MusicSource]:
        results = self._pytheos.api.call('browse', 'get_source_info', sid=source_id)
        if results.header.result == 'success':
            return MusicSource(results.payload.vars)

        return None

