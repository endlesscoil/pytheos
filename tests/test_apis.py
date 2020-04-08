#!/usr/bin/env python
from __future__ import annotations

import os
import sys
import time

from pytheos.api.player.types import Player, MediaItem, PlayMode, QuickSelect, ShuffleMode, RepeatMode
from pytheos.errors import CommandFailedError

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
        self._pytheos.api.system.register_for_change_events(True)

    def test_system_check_account(self):
        self.assertTrue(self._pytheos.api.system.check_account())

    @unittest.skip('Too disruptive')
    def test_system_sign_in(self):
        self._pytheos.api.system.sign_in()

    @unittest.skip('Too disruptive')
    def test_system_sign_out(self):
        self._pytheos.api.system.sign_out()

    def test_system_heart_beat(self):
        self._pytheos.api.system.heart_beat()

    @unittest.skip('Too disruptive')
    def test_system_reboot(self):
        self._pytheos.api.system.reboot()

    def test_system_prettify_json_response(self):
        for enable in (True, False):
            self._pytheos.api.system.prettify_json_response(enable)

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
        self.assertIn(play_state, ('play', 'pause', 'stop'))

    def test_player_set_play_state(self):
        pid = self._get_pid_to_query()
        for state in ('play', 'pause', 'stop'):
            self._pytheos.api.player.set_play_state(pid, state)
            time.sleep(1)

        self.assertRaises(ValueError, self._pytheos.api.player.set_play_state, pid, 'invalid_state')

    def test_player_get_now_playing_media(self):
        pid = self._get_pid_to_query()
        now_playing = self._pytheos.api.player.get_now_playing_media(pid) # FIXME?: What about the options?
        self.assertIsInstance(now_playing, MediaItem)

    def test_player_get_volume(self):
        pid = self._get_pid_to_query()
        volume = self._pytheos.api.player.get_volume(pid)
        self.assertIsInstance(volume, int)
        self.assertTrue(0 <= volume <= 100)

    def test_player_set_volume(self):
        pid = self._get_pid_to_query()
        self._pytheos.api.player.set_volume(pid, 20)
        self.assertRaises(ValueError, self._pytheos.api.player.set_volume, pid, 101)
        self.assertRaises(ValueError, self._pytheos.api.player.set_volume, pid, -1)

    def test_player_volume_up(self):
        pid = self._get_pid_to_query()
        self._pytheos.api.player.volume_up(pid, 5)
        self.assertRaises(ValueError, self._pytheos.api.player.volume_up, pid, 11)
        self.assertRaises(ValueError, self._pytheos.api.player.volume_up, pid, 0)

    def test_player_volume_down(self):
        pid = self._get_pid_to_query()
        self._pytheos.api.player.volume_down(pid, 5)
        self.assertRaises(ValueError, self._pytheos.api.player.volume_down, pid, 11)
        self.assertRaises(ValueError, self._pytheos.api.player.volume_down, pid, 0)

    def test_player_get_mute(self):
        pid = self._get_pid_to_query()
        muted = self._pytheos.api.player.get_mute(pid)
        self.assertIsInstance(muted, bool)

    def test_player_set_mute(self):
        pid = self._get_pid_to_query()
        for enable in (True, False):
            self._pytheos.api.player.set_mute(pid, enable)

    def test_player_toggle_mute(self):
        pid = self._get_pid_to_query()
        self._pytheos.api.player.toggle_mute(pid)

    def test_player_get_play_mode(self):
        pid = self._get_pid_to_query()
        play_mode = self._pytheos.api.player.get_play_mode(pid)
        self.assertIsInstance(play_mode, PlayMode)

    def test_player_set_play_mode(self):
        pid = self._get_pid_to_query()
        self._pytheos.api.player.set_play_mode(pid, PlayMode(repeat=RepeatMode.Off, shuffle=ShuffleMode.Off)) # Don't really need to test the others

    def test_player_get_queue(self):
        pid = self._get_pid_to_query()
        # FIXME: construct queue
        queue = self._pytheos.api.player.get_queue(pid, 0, 10)
        self.assertIsInstance(queue, list)
        self.assertGreater(len(queue), 0)
        self.assertIsInstance(queue[0], MediaItem)

        self.assertRaises(ValueError, self._pytheos.api.player.get_queue, pid, -1, 10)  # Lower limit too small
        self.assertRaises(ValueError, self._pytheos.api.player.get_queue, pid, 0, 101)  # Number to retrieve too large
        self.assertRaises(ValueError, self._pytheos.api.player.get_queue, pid, 0, 0)    # Number to retrieve too small

    def test_player_play_queue(self):
        pid = self._get_pid_to_query()
        # FIXME: construct queue
        queue = self._pytheos.api.player.get_queue(pid)
        self.assertGreater(len(queue), 0)

        self._pytheos.api.player.play_queue(pid, queue[0].queue_id)

        self.assertRaises(CommandFailedError, self._pytheos.api.player.play_queue, pid, -1)

    def test_player_remove_from_queue(self):
        pid = self._get_pid_to_query()
        self._pytheos.api.player.remove_from_queue(pid, queue_ids=(0,))
        time.sleep(1)
        self._pytheos.api.player.remove_from_queue(pid, queue_ids=(0, 1))

    @unittest.skip("Too disruptive - and I don't know how to remove them yet")
    def test_player_save_queue(self):
        pid = self._get_pid_to_query()
        # FIXME: construct queue
        self._pytheos.api.player.save_queue(pid, "Test Playlist")
        self.assertRaises(ValueError, self._pytheos.api.player.save_queue, pid, '*'*129)

    @unittest.skip('Too disruptive')
    def test_player_clear_queue(self):
        pid = self._get_pid_to_query()
        # FIXME: construct queue
        self._pytheos.api.player.clear_queue(pid)

    @unittest.skip('Too disruptive')
    def test_player_move_queue(self):
        pid = self._get_pid_to_query()
        # FIXME: construct queue
        queue = self._pytheos.api.player.get_queue(pid)
        self.assertGreater(len(queue), 2)

        self._pytheos.api.player.move_queue(pid, source_ids=(1,), destination_id=1)
        self._pytheos.api.player.move_queue(pid, source_ids=(1, 2), destination_id=3)

        self.assertRaises(ValueError, self._pytheos.api.player_move_queue, pid, source_ids=(-1,), destination_id=0) # Invalid source ID
        self.assertRaises(ValueError, self._pytheos.api.player_move_queue, pid, source_ids=(0,), destination_id=4)  # Invalid destination ID

    def test_player_play_next(self):
        pid = self._get_pid_to_query()
        # FIXME: construct queue
        self._pytheos.api.player.play_next(pid)

    def test_player_play_previous(self):
        pid = self._get_pid_to_query()
        # FIXME: construct queue
        self._pytheos.api.player.play_previous(pid)

    def test_player_set_quickselect(self):
        pid = self._get_pid_to_query()
        self._pytheos.api.player.set_quickselect(pid, 1)

        self.assertRaises(ValueError, self._pytheos.api.player.set_quickselect, pid, 0) # Value too small
        self.assertRaises(ValueError, self._pytheos.api.player.set_quickselect, pid, 7) # Value too large

    def test_player_play_quickselect(self):
        pid = self._get_pid_to_query()
        self._pytheos.api.player.play_quickselect(pid, 1)

        self.assertRaises(ValueError, self._pytheos.api.player.play_quickselect, pid, 0) # Value too small
        self.assertRaises(ValueError, self._pytheos.api.player.play_quickselect, pid, 7) # Value too large

    @unittest.skip('No AVR to test with')
    def test_player_get_quickselects(self):
        pid = self._get_pid_to_query()
        quick_selects = self._pytheos.api.player.get_quickselects(pid)
        self.assertIsInstance(quick_selects, list)
        self.assertGreater(len(quick_selects), 0)
        self.assertIsInstance(quick_selects[0], QuickSelect)

    def test_player_check_update(self):
        pid = self._get_pid_to_query()
        update_available = self._pytheos.api.player.check_update(pid)
        self.assertIsInstance(update_available, bool)

    # Utils
    def _get_pid_to_query(self):
        players = self._pytheos.api.player.get_players()
        self.assertGreater(len(players), 0)
        self.assertIsInstance(players[0], Player)

        return players[0].player_id


if __name__== '__main__':
    unittest.main()
