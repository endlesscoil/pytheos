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
        self.assertTrue(self._pytheos.api.system.register_for_change_events(True))

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
        self.assertTrue(self._pytheos.api.system.prettify_json_response(True))
        self.assertTrue(self._pytheos.api.system.prettify_json_response(False))

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
            new_state = self._pytheos.api.player.set_play_state(pid, state)
            self.assertEqual(new_state, state)

        self.assertRaises(ValueError, self._pytheos.api.player.set_play_state(pid, 'invalid_state'))

    def test_player_get_now_playing_media(self):
        pid = self._get_pid_to_query()
        now_playing = self._pytheos.api.player.get_now_playing_media(pid) # FIXME?: What about the options?
        self.assertIsInstance(now_playing, MediaDetails)

    def test_player_get_volume(self):
        pid = self._get_pid_to_query()
        volume = self._pytheos.api.player.get_volume(pid)
        self.assertIsInstance(volume, int)
        self.assertTrue(0 <= volume <= 100)

    def test_player_set_volume(self):
        pid = self._get_pid_to_query()
        new_volume = self._pytheos.api.player.set_volume(pid, 20)
        self.assertIsInstance(new_volume, int)
        self.assertTrue(0 <= new_volume <= 100)
        self.assertRaises(ValueError, self._pytheos.api.player.set_volume(pid, 101))
        self.assertRaises(ValueError, self._pytheos.api.player.set_volume(pid, -1))

    def test_player_volume_up(self):
        pid = self._get_pid_to_query()
        step_level = self._pytheos.api.player.volume_up(pid, 5)
        self.assertIsInstance(step_level, int)
        self.assertTrue(1 <= step_level <= 10)
        self.assertRaises(ValueError, self._pytheos.api.player.volume_up(pid, 11))
        self.assertRaises(ValueError, self._pytheos.api.player.volume_up(pid, 0))

    def test_player_volume_down(self):
        pid = self._get_pid_to_query()
        step_level = self._pytheos.api.player.volume_down(pid, 5)
        self.assertIsInstance(step_level, int)
        self.assertTrue(1 <= step_level <= 10)
        self.assertRaises(ValueError, self._pytheos.api.player.volume_down(pid, 11))
        self.assertRaises(ValueError, self._pytheos.api.player.volume_down(pid, 0))

    def test_player_get_mute(self):
        pid = self._get_pid_to_query()
        muted = self._pytheos.api.player.get_mute(pid)
        self.assertIsInstance(muted, bool)

    def test_player_set_mute(self):
        pid = self._get_pid_to_query()
        muted = self._pytheos.api.player.set_mute(pid, True)
        self.assertIsInstance(muted, bool)

    def test_player_toggle_mute(self):
        pid = self._get_pid_to_query()
        success = self._pytheos.api.player.toggle_mute(pid)
        self.assertIsInstance(success, bool)

    def test_player_get_play_mode(self):
        pid = self._get_pid_to_query()
        play_mode = self._pytheos.api.player.get_play_mode(pid)
        self.assertIsInstance(play_mode, PlayMode)

    def test_player_set_play_mode(self):
        pid = self._get_pid_to_query()
        success = self._pytheos.api.player.set_play_mode(pid, repeat='off', shuffle='off') # Don't really need to test the others
        self.assertIsInstance(success, bool)

    def test_player_get_queue(self):
        pid = self._get_pid_to_query()
        queue = self._pytheos.api.player.get_queue(pid)
        self.assertIsInstance(queue, list)
        if queue:
            self.assertIsInstance(queue[0], QueueItem)

        queue = self._pytheos.api.player.get_queue(pid, 0, 10)
        self.assertIsInstance(queue, list)

        self.assertRaises(ValueError, self._pytheos.api.player.get_queue(pid, -1, 10))  # Lower limit too small
        self.assertRaises(ValueError, self._pytheos.api.player.get_queue(pid, 0, 100))  # Upper limit too large
        self.assertRaises(ValueError, self._pytheos.api.player.get_queue(pid, 10, 1))   # Lower limit > upper limit

    def test_player_play_queue(self):
        pid = self._get_pid_to_query()
        queue = self._pytheos.api.player.get_queue(pid)
        self.assertGreater(len(queue), 0)

        success = self._pytheos.api.player.play_queue(pid, queue[0].id)
        self.assertTrue(success)

        success = self._pytheos.api.player.play_queue(pid, -1)
        self.assertFalse(success)

    def test_player_remove_from_queue(self):
        pid = self._get_pid_to_query()
        queue = self._pytheos.api.player.get_queue(pid)
        self.assertGreater(len(queue), 2)

        queue_ids = [item.id for item in queue]
        success = self._pytheos.api.player.remove_from_queue(pid, queue_ids=queue_ids[0])
        self.assertTrue(success)

        success = self._pytheos.api.player.remove_from_queue(pid, queue_ids=queue_ids[1:2])
        self.assertTrue(success)

        success = self._pytheos.api.player.remove_from_queue(pid, queue_ids=(-1,))
        self.assertFalse(success)

    def test_player_save_queue(self):
        pid = self._get_pid_to_query()
        success = self._pytheos.api.player.save_queue(pid, "Test Playlist")
        self.assertTrue(success)

    def test_player_clear_queue(self):
        pid = self._get_pid_to_query()
        success = self._pytheos.api.player.clear_queue(pid)
        self.assertTrue(success)

    def test_player_move_queue(self):
        pid = self._get_pid_to_query()
        queue = self._pytheos.api.player.get_queue(pid)
        self.assertGreater(len(queue), 2)

        success = self._pytheos.api.player.move_queue(pid, source_ids=(1,), destination_id=1)
        self.assertTrue(success)

        success = self._pytheos.api.player.move_queue(pid, source_ids=(1, 2), destination_id=3)
        self.assertTrue(success)

        self.assertRaises(ValueError, self._pytheos.api.player_move_queue(pid, source_ids=(-1,), destination_id=0)) # Invalid source ID
        self.assertRaises(ValueError, self._pytheos.api.player_move_queue(pid, source_ids=(0,), destination_id=4))  # Invalid destination ID

    def test_player_play_next(self):
        pid = self._get_pid_to_query()
        success = self._pytheos.api.player.play_next(pid)
        self.assertIsInstance(success, bool)

    def test_player_play_previous(self):
        pid = self._get_pid_to_query()
        success = self._pytheos.api.player.play_previous(pid)
        self.assertIsInstance(success, bool)

    def test_player_set_quickselect(self):
        pid = self._get_pid_to_query()
        success = self._pytheos.api.player.set_quickselect(pid, 1)
        self.assertTrue(success)

        self.assertRaises(ValueError, self._pytheos.api.player.set_quickselect(pid, 0)) # Value too small
        self.assertRaises(ValueError, self._pytheos.api.player.set_quickselect(pid, 7)) # Value too large

    def test_player_play_quickselect(self):
        pid = self._get_pid_to_query()
        success = self._pytheos.api.player.play_quickselect(pid, 1)
        self.assertTrue(success)

        self.assertRaises(ValueError, self._pytheos.api.player.play_quickselect(pid, 0)) # Value too small
        self.assertRaises(ValueError, self._pytheos.api.player.play_quickselect(pid, 7)) # Value too large

    def test_player_get_quickselects(self):
        pid = self._get_pid_to_query()
        quickselects = self._pytheos.api.player.get_quickselects(pid)
        self.assertIsInstance(quickselects, list)
        self.assertGreater(len(quickselects), 0)
        self.assertIsInstance(quickselects[0], QuickSelect)

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
