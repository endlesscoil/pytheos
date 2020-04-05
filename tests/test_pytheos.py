#!/usr/bin/env python
from __future__ import annotations

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..")) # FIXME

import unittest
import pytheos


class TestPytheos(unittest.TestCase):
    def setUp(self) -> None:
        self._pytheos = pytheos.Pytheos('10.7.2.64', 1255)
        self._pytheos.connect()

    def tearDown(self) -> None:
        self._pytheos.close()

    def test_discover(self):
        discovered = pytheos.discover()
        self.assertIsInstance(discovered[0], pytheos.Pytheos)

    def test_connect(self):
        server = '10.7.2.64:1255'

        with pytheos.connect(server) as connection:
            self.assertIsNotNone(connection)

    def test_system_heartbeat(self):
        self._pytheos.call('system', 'heart_beat')


if __name__== '__main__':
    unittest.main()
