#!/usr/bin/env python
from pytheos.api.group.types import Group


class PytheosGroup:
    def __init__(self, pytheos, group: Group):
        self._pytheos = pytheos
        self._group = group
