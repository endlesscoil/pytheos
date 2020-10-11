#!/usr/bin/env python
from pytheos.logger import logger

from .pytheos import Pytheos, connect
from .discovery import discover


def set_log_level(level: int):
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


__all__ = ['Pytheos', 'connect', 'discover']
