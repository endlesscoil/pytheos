#!/usr/bin/env python
from pytheos.api.browse.types import MusicSource


class PytheosSource:
    def __init__(self, pytheos, source: MusicSource):
        self._pytheos = pytheos
        self._source = source
