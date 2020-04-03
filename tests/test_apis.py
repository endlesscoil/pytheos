#!/usr/bin/env python
import os
import sys

from pytheos.api.player.types import Player

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..")) # FIXME

import unittest
import pytheos


class TestAPIs(unittest.TestCase):
    def setUp(self) -> None:
        self._pytheos = pytheos.Pytheos('10.7.2.64', 1255)
        self._pytheos.connect()

    def tearDown(self) -> None:
        self._pytheos.close()

    def test_system_register_for_change_events(self):
        self.assertTrue(self._pytheos.api.system.register_for_change_events(enable='on'))

    def test_system_check_account(self):
        self.assertTrue(self._pytheos.api.system.check_account())

    @unittest.skip('Too annoying')
    def test_system_sign_in(self):
        self.assertTrue(self._pytheos.api.system.sign_in())

    @unittest.skip('Too annoying')
    def test_system_sign_out(self):
        self.assertTrue(self._pytheos.api.system.sign_out())

    def test_system_heart_beat(self):
        self.assertTrue(self._pytheos.api.system.heart_beat())

    @unittest.skip('Too iffy')
    def test_system_reboot(self):
        self.assertTrue(self._pytheos.api.system.reboot())

    def test_system_prettify_json_response(self):
        self.assertTrue(self._pytheos.api.system.prettify_json_response(enable='on'))

    def test_player_get_players(self):
        players = self._pytheos.api.player.get_players()
        self.assertGreater(len(players), 0)
        self.assertIsInstance(players[0], Player)

    def test_player_get_player_info(self):
        pid = self._get_pid_to_query()
        self.assertIsInstance(self._pytheos.api.player.get_player_info(pid), Player)

    def test_player_get_play_state(self):
        pid = self._get_pid_to_query()
        play_state = self._pytheos.api.player.get_play_state(pid)
        self.assertIsNotNone(play_state)

    def _get_pid_to_query(self):
        players = self._pytheos.api.player.get_players()
        self.assertGreater(len(players), 0)
        self.assertIsInstance(players[0], Player)

        return players[0].pid


if __name__== '__main__':
    unittest.main()
