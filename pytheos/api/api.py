#!/usr/bin/env python
""" Base API implementation """

from __future__ import annotations


class API:
    """ Base API implementation """
    def __init__(self, pytheos_object):
        self._api = pytheos_object
