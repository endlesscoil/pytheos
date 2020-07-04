#!/usr/bin/env python
from pytheos.api.player.types import Player


class PytheosPlayer:
    def __init__(self, pytheos, player: Player):
        self._pytheos = pytheos
        self._player = player

