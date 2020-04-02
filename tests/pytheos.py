#!/usr/bin/env python
import unittest

import pytheos
from pytheos import Pytheos


class TestPytheos(unittest.TestCase):
    def setUp(self) -> None:
        self._pytheos = Pytheos()

    def test_discover(self):
        discovered = pytheos.discover()
        self.assertGreater(len(discovered), 0)

    def test_connect(self):
        server = 'localhost'

        with pytheos.connect(server) as connection:
            self.assertIsNotNone(connection)

    def test_command(self):
        self._pytheos.execute('player', 'something', some_arg=True)

if __name__== '__main__':
    unittest.main()
