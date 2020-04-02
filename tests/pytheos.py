#!/usr/bin/env python
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
        discovered = pytheos.discover("urn:schemas-denon-com:device:ACT-Denon:1")
        self.assertIsInstance(discovered[0], pytheos.Pytheos)

    def test_connect(self):
        server = '10.7.2.64:1255'

        with pytheos.connect(server) as connection:
            self.assertIsNotNone(connection)

    def test_system_heartbeat(self):
        header, payload = self._pytheos.call('system', 'heart_beat')
        self.assertTrue(header.succeeded)

    # def test_foo(self):
    #     import time
    #
    #     while True:
    #         time.sleep(0.5)


if __name__== '__main__':
    unittest.main()
