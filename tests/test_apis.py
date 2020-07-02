#!/usr/bin/env python
from __future__ import annotations

import os
import sys
import time

import unittest
from unittest.mock import patch

from pytheos.api.types import Mute

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pytheos.api.browse.types import MusicSource, SourceMedia, SearchCriteria, InputSource, AddToQueueType, \
    AlbumMetadata, ServiceOption
from pytheos.api.group.group import GroupAPI
from pytheos.api.group.types import Group
from pytheos.api.player.types import Player, MediaItem, PlayMode, QuickSelect, ShuffleMode, RepeatMode, PlayState
from pytheos.errors import CommandFailedError, SignInFailedError

import pytheos
import pytheos.connection

TEST_PLAYER_ID = 12345678


class TestAPIs(unittest.TestCase):
    def setUp(self):
        self._pytheos = pytheos.Pytheos('127.0.0.1', 1255)
        self._pytheos.api.send_command = unittest.mock.MagicMock()

    def test_system_register_for_change_events(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "system/register_for_change_events",
                                  "result": "success", "message": "enable=on"
                              }
                          }) as mock:
            self._pytheos.api.system.register_for_change_events(True)
            self._pytheos.api.send_command.assert_called_with('system', 'register_for_change_events', enable='on')

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "system/register_for_change_events",
                                  "result": "success", "message": "enable=off"
                              }
                          }) as mock:
            self._pytheos.api.system.register_for_change_events(False)
            self._pytheos.api.send_command.assert_called_with('system', 'register_for_change_events', enable='off')

    def test_system_check_account(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "system/check_account",
                                  "result": "success",
                                  "message": "signed_in&un=username@someemailplace.com"
                              }
                          }) as mock:
            status, email = self._pytheos.api.system.check_account()
            self.assertEqual(status, 'signed_in')
            self.assertEqual(email, 'username@someemailplace.com')
            self._pytheos.api.send_command.assert_called_with('system', 'check_account')

    def test_system_sign_in(self):
        username = 'username@someemailplace.com'
        password = 'somepassword'

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "system/sign_in",
                                  "result": "success",
                                  "message": "signed_in&un=username@someemailplace.com"
                              }
                          }) as mock:
            self._pytheos.api.system.sign_in(username, password)
            self._pytheos.api.send_command.assert_called_with('system', 'sign_in', un=username, pw=password)

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "system/sign_in",
                                  "result": "fail",
                                  "message": ""
                              }
                          }) as mock:
            self.assertRaises(SignInFailedError, self._pytheos.api.system.sign_in, username, password)

    def test_system_sign_out(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "system/sign_out",
                                  "result": "success",
                                  "message": "signed_out"
                              }
                          }) as mock:
            self._pytheos.api.system.sign_out()
            self._pytheos.api.send_command.assert_called_with('system', 'sign_out')

    def test_system_heart_beat(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "system/heart_beat",
                                  "result": "success",
                                  "message": ""
                              }
                          }) as mock:
            self._pytheos.api.system.heart_beat()
            self._pytheos.api.send_command.assert_called_with('system', 'heart_beat')

    def test_system_reboot(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message', return_value=None) as mock:
            self._pytheos.api.system.reboot()
            self._pytheos.api.send_command.assert_called_with('system', 'reboot')

    def test_system_prettify_json_response(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "system/prettify_json_response",
                                  "result": "success",
                                  "message": "enable=on",
                              }
                          }) as mock:
                self._pytheos.api.system.prettify_json_response(True)
                self._pytheos.api.send_command.assert_called_with('system', 'prettify_json_response', enable='on')

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "system/prettify_json_response",
                                  "result": "success",
                                  "message": "enable=off",
                              }
                          }) as mock:
                self._pytheos.api.system.prettify_json_response(False)
                self._pytheos.api.send_command.assert_called_with('system', 'prettify_json_response', enable='off')

    def test_player_get_players(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/get_players",
                                  "result": "success",
                                  "message": ""
                              },
                              "payload": [
                                  {
                                      "name": "Marantz PM7000N",
                                      "pid": TEST_PLAYER_ID,
                                      "model": "Marantz PM7000N",
                                      "version": "1.562.230",
                                      "ip": "10.10.0.7",
                                      "network": "wifi",
                                      "lineout": 0,
                                      "serial": "SN12345678"
                                  }
                              ]
                          }) as mock:
            players = self._pytheos.api.player.get_players()
            self.assertGreater(len(players), 0)
            self.assertIsInstance(players[0], Player)

    def test_player_get_player_info(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/get_player_info",
                                  "result": "success",
                                  "message": ""
                              },
                              "payload": [
                                  {
                                      "name": "Marantz PM7000N",
                                      "pid": TEST_PLAYER_ID,
                                      "model": "Marantz PM7000N",
                                      "version": "1.562.230",
                                      "ip": "10.10.0.7",
                                      "network": "wifi",
                                      "lineout": 0,
                                      "serial": "SN12345678"
                                  }
                              ]
                          }) as mock:
            result = self._pytheos.api.player.get_player_info(TEST_PLAYER_ID)
            self._pytheos.api.send_command.assert_called_with('player', 'get_player_info', pid=TEST_PLAYER_ID)
            self.assertIsInstance(result, Player)

    def test_player_get_play_state(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/get_play_state",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&state=stop"
                              },
                          }) as mock:
            play_state = self._pytheos.api.player.get_play_state(TEST_PLAYER_ID)
            self._pytheos.api.send_command.assert_called_with('player', 'get_play_state', pid=TEST_PLAYER_ID)
            self.assertEqual(play_state, PlayState.Stopped)

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/get_play_state",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&state=play"
                              },
                          }) as mock:
            play_state = self._pytheos.api.player.get_play_state(TEST_PLAYER_ID)
            self._pytheos.api.send_command.assert_called_with('player', 'get_play_state', pid=TEST_PLAYER_ID)
            self.assertEqual(play_state, PlayState.Playing)

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/get_play_state",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&state=pause"
                              },
                          }) as mock:
            play_state = self._pytheos.api.player.get_play_state(TEST_PLAYER_ID)
            self._pytheos.api.send_command.assert_called_with('player', 'get_play_state', pid=TEST_PLAYER_ID)
            self.assertEqual(play_state, PlayState.Paused)

    def test_player_set_play_state(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/set_play_state",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&state=stop"
                              },
                          }) as mock:
            self._pytheos.api.player.set_play_state(TEST_PLAYER_ID, PlayState.Stopped)
            self._pytheos.api.send_command.assert_called_with('player', 'set_play_state', pid=TEST_PLAYER_ID, state=PlayState.Stopped)

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/set_play_state",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&state=play"
                              },
                          }) as mock:
            self._pytheos.api.player.set_play_state(TEST_PLAYER_ID, PlayState.Playing)
            self._pytheos.api.send_command.assert_called_with('player', 'set_play_state', pid=TEST_PLAYER_ID, state=PlayState.Playing)

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/set_play_state",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&state=pause"
                              },
                          }) as mock:
            self._pytheos.api.player.set_play_state(TEST_PLAYER_ID, PlayState.Paused)
            self._pytheos.api.send_command.assert_called_with('player', 'set_play_state', pid=TEST_PLAYER_ID, state=PlayState.Paused)

        self.assertRaises(ValueError, self._pytheos.api.player.set_play_state, TEST_PLAYER_ID, 'invalid_state')

    def test_player_get_now_playing_media(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/get_now_playing_media",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}"
                              }, "payload": {
                                  "type": "station",
                                  "song": "TOOL Radio",
                                  "station": "TOOL Radio",
                                  "album": "",
                                  "artist": "",
                                  "image_url": "https://content-images.p-cdn.com/images/c2/e4/83/44/bd064cd5943ec627b04cc04e/_500W_500H.jpg",
                                  "album_id": "",
                                  "mid": "4525086864314761798",
                                  "qid": 1,
                                  "sid": 1
                              },
                              "options": [
                                  {
                                      "play": [
                                          {"id": 11, "name": "Thumbs Up"},
                                          {"id": 12, "name": "Thumbs Down"},
                                          {"id": 19, "name": "Add to HEOS Favorites"}
                                      ]
                                  }
                              ]
                          }) as mock:
            now_playing = self._pytheos.api.player.get_now_playing_media(TEST_PLAYER_ID) # FIXME?: What about the options?
            self._pytheos.api.send_command.assert_called_with('player', 'get_now_playing_media', pid=TEST_PLAYER_ID)
            self.assertIsInstance(now_playing, MediaItem)

    def test_player_get_volume(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/get_volume",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&level=10"
                              },
                          }) as mock:
            volume = self._pytheos.api.player.get_volume(TEST_PLAYER_ID)
            self._pytheos.api.send_command.assert_called_with('player', 'get_volume', pid=TEST_PLAYER_ID)
            self.assertEqual(volume, 10)

    def test_player_set_volume(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/set_volume",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&level=20"
                              },
                          }) as mock:
            self._pytheos.api.player.set_volume(TEST_PLAYER_ID, 20)
            self._pytheos.api.send_command.assert_called_with('player', 'set_volume', pid=TEST_PLAYER_ID, level=20)

        self.assertRaises(ValueError, self._pytheos.api.player.set_volume, TEST_PLAYER_ID, 101)
        self.assertRaises(ValueError, self._pytheos.api.player.set_volume, TEST_PLAYER_ID, -1)

    def test_player_volume_up(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/volume_up",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&step=5"
                              },
                          }) as mock:
            self._pytheos.api.player.volume_up(TEST_PLAYER_ID, 5)
            self._pytheos.api.send_command.assert_called_with('player', 'volume_up', pid=TEST_PLAYER_ID, step=5)

        self.assertRaises(ValueError, self._pytheos.api.player.volume_up, TEST_PLAYER_ID, 11)
        self.assertRaises(ValueError, self._pytheos.api.player.volume_up, TEST_PLAYER_ID, 0)

    def test_player_volume_down(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/volume_down",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&step=5"
                              },
                          }) as mock:
            self._pytheos.api.player.volume_down(TEST_PLAYER_ID, 5)
            self._pytheos.api.send_command.assert_called_with('player', 'volume_down', pid=TEST_PLAYER_ID, step=5)

        self.assertRaises(ValueError, self._pytheos.api.player.volume_down, TEST_PLAYER_ID, 11)
        self.assertRaises(ValueError, self._pytheos.api.player.volume_down, TEST_PLAYER_ID, 0)

    def test_player_get_mute(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/get_mute",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&state=off"
                              },
                          }) as mock:
            muted = self._pytheos.api.player.get_mute(TEST_PLAYER_ID)
            self._pytheos.api.send_command.assert_called_with('player', 'get_mute', pid=TEST_PLAYER_ID)
            self.assertEqual(muted, False)

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/get_mute",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&state=on"
                              },
                          }) as mock:
            muted = self._pytheos.api.player.get_mute(TEST_PLAYER_ID)
            self._pytheos.api.send_command.assert_called_with('player', 'get_mute', pid=TEST_PLAYER_ID)
            self.assertEqual(muted, True)

    def test_player_set_mute(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/set_mute",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&state=on"
                              },
                          }) as mock:
            self._pytheos.api.player.set_mute(TEST_PLAYER_ID, True)
            self._pytheos.api.send_command.assert_called_with('player', 'set_mute', pid=TEST_PLAYER_ID, state=Mute.On)

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/set_mute",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&state=off"
                              },
                          }) as mock:
            self._pytheos.api.player.set_mute(TEST_PLAYER_ID, False)
            self._pytheos.api.send_command.assert_called_with('player', 'set_mute', pid=TEST_PLAYER_ID, state=Mute.Off)

    def test_player_toggle_mute(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/toggle_mute",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}"
                              },
                          }) as mock:
            self._pytheos.api.player.toggle_mute(TEST_PLAYER_ID)
            self._pytheos.api.send_command.assert_called_with('player', 'toggle_mute', pid=TEST_PLAYER_ID)

    def test_player_get_play_mode(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/get_play_mode",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&repeat=off&shuffle=off"
                              },
                          }) as mock:
            play_mode = self._pytheos.api.player.get_play_mode(TEST_PLAYER_ID)
            self._pytheos.api.send_command.assert_called_with('player', 'get_play_mode', pid=TEST_PLAYER_ID)
            self.assertIsInstance(play_mode, PlayMode)
            self.assertEqual(play_mode.repeat, RepeatMode.Off)
            self.assertEqual(play_mode.shuffle, ShuffleMode.Off)

    def test_player_set_play_mode(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/set_play_mode",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&repeat=off&shuffle=off"
                              },
                          }) as mock:
            self._pytheos.api.player.set_play_mode(TEST_PLAYER_ID, PlayMode(repeat=RepeatMode.Off, shuffle=ShuffleMode.Off))
            self._pytheos.api.send_command.assert_called_with('player', 'set_play_mode', pid=TEST_PLAYER_ID, repeat=RepeatMode.Off, shuffle=ShuffleMode.Off)

    def test_player_get_queue(self):
        start_pos = 0
        retrieve_count = 10

        with patch.object(pytheos.api.interface.APIInterface, 'read_message', return_value=self._get_demo_queue()) as mock:
            queue = self._pytheos.api.player.get_queue(TEST_PLAYER_ID, start_pos, retrieve_count)
            self._pytheos.api.send_command.assert_called_with('player', 'get_queue',
                                                              pid=TEST_PLAYER_ID,
                                                              range=','.join((str(start_pos), str(retrieve_count - 1))))
            self.assertIsInstance(queue, list)
            self.assertGreater(len(queue), 0)
            self.assertIsInstance(queue[0], MediaItem)

        self.assertRaises(ValueError, self._pytheos.api.player.get_queue, TEST_PLAYER_ID, -1, 10)  # Lower limit too small
        self.assertRaises(ValueError, self._pytheos.api.player.get_queue, TEST_PLAYER_ID, 0, 101)  # Number to retrieve too large
        self.assertRaises(ValueError, self._pytheos.api.player.get_queue, TEST_PLAYER_ID, 0, 0)    # Number to retrieve too small

    def test_player_play_queue(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message', return_value=self._get_demo_queue()) as mock:
            queue = self._pytheos.api.player.get_queue(TEST_PLAYER_ID, 0, 10)

            self._pytheos.api.player.play_queue(TEST_PLAYER_ID, queue[0].queue_id)
            self._pytheos.api.send_command.assert_called_with('player', 'play_queue', pid=TEST_PLAYER_ID, qid=queue[0].queue_id)

        self.assertRaises(CommandFailedError, self._pytheos.api.player.play_queue, TEST_PLAYER_ID, -1)

    def test_player_remove_from_queue(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/remove_from_queue",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&qid=0"
                              },
                          }) as mock:
            self._pytheos.api.player.remove_from_queue(TEST_PLAYER_ID, queue_ids=(0,))
            self._pytheos.api.send_command.assert_called_with('player', 'remove_from_queue', pid=TEST_PLAYER_ID, qid='0')

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/remove_from_queue",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&qid=0,1"
                              },
                          }) as mock:
            self._pytheos.api.player.remove_from_queue(TEST_PLAYER_ID, queue_ids=(0, 1))
            self._pytheos.api.send_command.assert_called_with('player', 'remove_from_queue', pid=TEST_PLAYER_ID, qid='0,1')

    def test_player_save_queue(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/save_queue",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&name=Test Playlist"
                              },
                          }) as mock:
            self._pytheos.api.player.save_queue(TEST_PLAYER_ID, "Test Playlist")
            self._pytheos.api.send_command.assert_called_with('player', 'save_queue',
                                                              pid=TEST_PLAYER_ID, name='Test Playlist')

        self.assertRaises(ValueError, self._pytheos.api.player.save_queue, TEST_PLAYER_ID, '*'*129)

    def test_player_clear_queue(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/save_queue",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&name=Test Playlist"
                              },
                          }) as mock:
            self._pytheos.api.player.clear_queue(TEST_PLAYER_ID)
            self._pytheos.api.send_command.assert_called_with('player', 'clear_queue', pid=TEST_PLAYER_ID)

    def test_player_move_queue_item(self):
        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/move_queue_item",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&sqid=1&dqid=1"
                              },
                          }) as mock:
            self._pytheos.api.player.move_queue_item(TEST_PLAYER_ID, queue_ids=(1,), destination_queue_id=1)
            self._pytheos.api.send_command.assert_called_with('player', 'move_queue_item', pid=TEST_PLAYER_ID, sqid='1', dqid=1)

        with patch.object(pytheos.api.interface.APIInterface, 'read_message',
                          return_value={
                              "heos": {
                                  "command": "player/move_queue_item",
                                  "result": "success",
                                  "message": f"pid={TEST_PLAYER_ID}&sqid=1&dqid=1"
                              },
                          }) as mock:
            self._pytheos.api.player.move_queue_item(TEST_PLAYER_ID, queue_ids=(1, 2), destination_queue_id=3)
            self._pytheos.api.send_command.assert_called_with('player', 'move_queue_item', pid=TEST_PLAYER_ID, sqid='1,2', dqid=3)

        self.assertRaises(ValueError, self._pytheos.api.player.move_queue_item, TEST_PLAYER_ID, queue_ids=(1,), destination_queue_id=0)  # Invalid destination ID
        self.assertRaises(ValueError, self._pytheos.api.player.move_queue_item, TEST_PLAYER_ID, queue_ids=(0,), destination_queue_id=4)  # Invalid source ID

    def test_player_play_next(self):
        pid = self._get_pid_to_query()
        # FIXME: construct queue
        self._pytheos.api.player.play_next(pid)

    def test_player_play_previous(self):
        pid = self._get_pid_to_query()
        # FIXME: construct queue
        self._pytheos.api.player.play_previous(pid)

    @unittest.skip('No AVR to test with')
    def test_player_set_quickselect(self):
        pid = self._get_pid_to_query()
        self._pytheos.api.player.set_quickselect(pid, 1)

        self.assertRaises(ValueError, self._pytheos.api.player.set_quickselect, pid, 0) # Value too small
        self.assertRaises(ValueError, self._pytheos.api.player.set_quickselect, pid, 7) # Value too large

    @unittest.skip('No AVR to test with')
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

    @unittest.skip('No groups defined currently')
    def test_group_get_groups(self):
        groups = self._pytheos.api.group.get_groups()
        self.assertGreater(len(groups), 0)
        self.assertIsInstance(groups[0], GroupAPI)

    @unittest.skip('No groups defined currently')
    def test_group_get_group_info(self):
        gid = self._get_gid_to_query()
        group_info = self._pytheos.api.group.get_group_info(gid)
        self.assertIsInstance(group_info, GroupAPI)

        self.assertRaises(CommandFailedError, self._pytheos.api.group.get_group_info(-1))

    @unittest.skip('No groups defined currently')
    def test_group_set_group(self):
        leader = self._get_pid_to_query()
        members = [0, 1] # FIXME - use real ids.
        results = self._pytheos.api.group.set_group(leader, members)
        self.assertIsInstance(results, Group)

        # FIXME: needs to test removal cases.

        results = self._pytheos.api.group.set_group(leader)
        self.assertIsNone(results)

    @unittest.skip('No groups defined currently')
    def test_group_get_volume(self):
        gid = self._get_gid_to_query()
        volume = self._pytheos.api.group.get_volume(gid)
        self.assertIsInstance(volume, int)
        self.assertTrue(0 <= volume <= 100)

    @unittest.skip('No groups defined currently')
    def test_group_set_volume(self):
        gid = self._get_gid_to_query()
        self._pytheos.api.group.set_volume(gid, 20)
        self.assertRaises(ValueError, self._pytheos.api.group.set_volume, gid, 101)
        self.assertRaises(ValueError, self._pytheos.api.group.set_volume, gid, -1)

    @unittest.skip('No groups defined currently')
    def test_group_volume_up(self):
        gid = self._get_gid_to_query()
        self._pytheos.api.group.volume_up(gid, 5)
        self.assertRaises(ValueError, self._pytheos.api.group.volume_up, gid, 11)
        self.assertRaises(ValueError, self._pytheos.api.group.volume_up, gid, 0)

    @unittest.skip('No groups defined currently')
    def test_group_volume_down(self):
        gid = self._get_gid_to_query()
        self._pytheos.api.group.volume_down(gid, 5)
        self.assertRaises(ValueError, self._pytheos.api.group.volume_down, gid, 11)
        self.assertRaises(ValueError, self._pytheos.api.group.volume_down, gid, 0)

    @unittest.skip('No groups defined currently')
    def test_group_get_mute(self):
        gid = self._get_gid_to_query()
        muted = self._pytheos.api.group.get_mute(gid)
        self.assertIsInstance(muted, bool)

    @unittest.skip('No groups defined currently')
    def test_group_set_mute(self):
        gid = self._get_gid_to_query()
        for enable in (True, False):
            self._pytheos.api.group.set_mute(gid, enable)

    @unittest.skip('No groups defined currently')
    def test_group_toggle_mute(self):
        gid = self._get_gid_to_query()
        self._pytheos.api.group.toggle_mute(gid)

    def test_browse_get_music_sources(self):
        music_sources = self._pytheos.api.browse.get_music_sources()
        self.assertGreater(len(music_sources), 0)
        self.assertIsInstance(music_sources[0], MusicSource)

    def test_browse_get_source_info(self):
        self.assertIsInstance(self._pytheos.api.browse.get_source_info(1), MusicSource)
        self.assertRaises(CommandFailedError, self._pytheos.api.browse.get_source_info, -1)

    def test_browse_browse_source(self):
        music_sources = self._pytheos.api.browse.get_music_sources()
        sid = music_sources[0].source_id

        results = self._pytheos.api.browse.browse_source(sid)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], SourceMedia)

    def test_browse_browse_source_container(self):
        sid = 1024 # FIXME - Local Music

        results = self._pytheos.api.browse.browse_source(sid)
        plex_server = results[0]

        results = self._pytheos.api.browse.browse_source(plex_server.source_id)
        music = results[1]

        results = self._pytheos.api.browse.browse_source_container(plex_server.source_id, music.container_id)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], SourceMedia)

    def test_browse_get_search_criteria(self):
        sid = 1024 # FIXME - Local Music

        results = self._pytheos.api.browse.browse_source(sid)
        plex_server = results[0]

        results = self._pytheos.api.browse.get_search_criteria(plex_server.source_id)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], SearchCriteria)

    def test_browse_search(self):
        sid = 1024 # FIXME - Local Music

        results = self._pytheos.api.browse.browse_source(sid)
        plex_server = results[0]

        criteria = self._pytheos.api.browse.get_search_criteria(plex_server.source_id)
        self.assertGreater(len(criteria), 0)

        results = self._pytheos.api.browse.search(plex_server.source_id, 'a', criteria[0].search_criteria_id)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], SourceMedia)

    def test_browse_play_station(self):
        pid = self._get_pid_to_query()
        sid = 1 # FIXME - Pandora

        pandora_sources = self._pytheos.api.browse.browse_source(sid)
        AtoZ = pandora_sources[1]

        stations = self._pytheos.api.browse.browse_source_container(sid, AtoZ.container_id)
        to_play = stations[0]

        self._pytheos.api.browse.play_station(pid, sid, AtoZ.container_id, to_play.media_id, to_play.name)

    def test_browse_play_preset(self):
        pid = self._get_pid_to_query()

        self.assertRaises(ValueError, self._pytheos.api.browse.play_preset, pid, 0)

        self._pytheos.api.browse.play_preset(pid, 1)

    def test_browse_play_input(self):
        pid = self._get_pid_to_query()

        self._pytheos.api.browse.play_input(pid, InputSource.Phono)

    def test_browse_play_url(self):
        pid = self._get_pid_to_query()
        url = 'http://www.hochmuth.com/mp3/Haydn_Cello_Concerto_D-1.mp3'

        self._pytheos.api.browse.play_url(pid, url)

    def test_browse_add_container_to_queue(self):
        pid = self._get_pid_to_query()
        sid = 1024 # FIXME: Plex
        cid = 'dc7e8002b2f0ef9ef21b' # FIXME: White Zombie - La Sexorcisto
        self._pytheos.api.browse.add_to_queue(pid, sid, cid, add_type=AddToQueueType.AddToEnd)
        # FIXME: Test other add types

    def test_browse_add_track_to_queue(self):
        pid = self._get_pid_to_query()
        sid = 1024  # FIXME: Plex
        cid = 'dc7e8002b2f0ef9ef21b'    # FIXME: White Zombie - La Sexorcisto
        mid = '6101de04f2cd63dc9676'    # FIXME: Knuckle Duster
        self._pytheos.api.browse.add_to_queue(pid, sid, cid, media_id=mid, add_type=AddToQueueType.AddToEnd)
        # FIXME: Test other add types

    @unittest.skip('Skipping for now.')
    def test_browse_rename_playlist(self):
        sid = 1025 # FIXME: Playlists
        new_name = 'testing'

        # FIXME: Create playlist

        playlists = self._pytheos.api.browse.browse_source(sid)
        self.assertGreater(len(playlists), 0)

        p = playlists[0]
        orig_name = p.name

        self._pytheos.api.browse.rename_playlist(sid, p.container_id, new_name)
        new_playlists = self._pytheos.api.browse.browse_source(sid)
        self.assertTrue(any([pl.name == new_name for pl in new_playlists]))

        self._pytheos.api.browse.rename_playlist(sid, p.container_id, orig_name)
        new_playlists = self._pytheos.api.browse.browse_source(sid)
        self.assertTrue(any([pl.name == new_name for pl in new_playlists]))

    @unittest.skip('Skipping for now.')
    def test_browse_delete_playlist(self):
        sid = 1025 # FIXME: Playlists
        # FIXME: Create playlist

        playlists = self._pytheos.api.browse.browse_source(sid)
        self.assertGreater(len(playlists), 0)
        p = playlists[0]

        self._pytheos.api.browse.delete_playlist(sid, p.container_id)
        new_playlists = self._pytheos.api.browse.browse_source(sid)
        self.assertTrue(len(new_playlists) == len(playlists) - 1)

    @unittest.skip("Meh, don't feel like dealing with Rhapsody or Napster.")
    def test_browse_retrieve_metadata(self):
        sid = 1 # FIXME
        cid = 1 # FIXME
        results = self._pytheos.api.browse.retrieve_metadata(sid, cid)
        self.assertEquals(results, AlbumMetadata)

    def test_browse_set_service_option(self):
        sid = 1 # FIXME: Pandora
        query = 'some band'
        results = self._pytheos.api.browse.set_service_option(sid, ServiceOption.CreateNewStation, name=query)
        self.assertGreater(int(results.header.vars.get('returned', 0)), 0)

    # Utils
    def _get_gid_to_query(self):
        groups = self._pytheos.api.group.get_groups()
        self.assertGreater(len(groups), 0)
        self.assertIsInstance(groups[0], GroupAPI)

        return groups[0].group_id

    def _get_demo_queue(self):
        return {
            "heos": {
              "command": "player/get_queue",
              "result": "success",
              "message": f"pid={TEST_PLAYER_ID}&range=0,99&returned=4&count=4"
            },
            "payload": [
              {
                  "song": "to bid you farewell",
                  "album": "Morningrise",
                  "artist": "Opeth",
                  "image_url": "http://10.10.0.7:32469/proxy/01c1ef4bb79e573b56e1/albumart.jpg",
                  "qid": 1,
                  "mid": "f82aa0f7d4f585460da5",
                  "album_id": "d51c42cba3d68cd59cc4"
              },
              {
                  "song": "The Apostle in Triumph",
                  "album": "Orchid",
                  "artist": "Opeth",
                  "image_url": "http://10.10.0.7:32469/proxy/97accac8b6d7d7e17d49/albumart.jpg",
                  "qid": 2,
                  "mid": "57c488a101cc7bd8727f",
                  "album_id": "aba54638f73286e151c3"
              },
              {
                  "song": "Hessian Peel",
                  "album": "Watershed",
                  "artist": "Opeth",
                  "image_url": "http://10.10.0.7:32469/proxy/c67c58dd9e036052b807/albumart.jpg",
                  "qid": 3,
                  "mid": "a56f574d9f92dc5c2ce1",
                  "album_id": "ec9f45094fd04b62b4cc"
              },
              {
                  "song": "Death Whispered a Lullaby",
                  "album": "Damnation",
                  "artist": "Opeth",
                  "image_url": "http://10.10.0.7:32469/proxy/b2c515a3703ed610eeff/albumart.jpg",
                  "qid": 4,
                  "mid": "fe9b44bd84603da68566",
                  "album_id": "23edbd4853d6c381e938"
              }
            ]
        }

if __name__== '__main__':
    unittest.main()
