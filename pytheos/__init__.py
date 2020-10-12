#!/usr/bin/env python
from .pytheos import Pytheos, connect
from .discovery import discover
from .logger import Logger


def set_log_level(level: int):
    Logger.setLevel(level)
    for handler in Logger.handlers:
        handler.setLevel(level)


__all__ = ['Pytheos', 'connect', 'discover']
