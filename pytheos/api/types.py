#!/usr/bin/env python
""" Provides type declarations related to the PlayerAPI group """
from __future__ import annotations

from enum import Enum


class Mute(Enum):
    On = 'on'
    Off = 'off'

    def __str__(self):
        return self.value
