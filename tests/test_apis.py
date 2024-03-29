#!/usr/bin/env python
from __future__ import annotations

import asyncio
import unittest
from typing import Union, List, Dict
from unittest import mock
from unittest.mock import patch

from pytheos.models.system import AccountStatus

from pytheos.models.browse import SearchCriteria, AddToQueueType, \
    AlbumMetadata, ServiceOption
from pytheos.models.source import Source, InputSource
from pytheos.models.media import MediaItem
from pytheos.models.group import Group, GroupRole, GroupPlayer
from pytheos.models.player import Player, PlayMode, QuickSelect, ShuffleMode, RepeatMode, PlayState, Mute
from pytheos.networking.errors import CommandFailedError, SignInFailedError

import pytheos
import pytheos.networking.connection


TEST_PLAYER_ID = 12345678
TEST_GROUP_ID = 1
TEST_EMAIL = "username@someemailplace.com"


def _async_run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestAPIs(unittest.TestCase):
    def setUp(self):
        self._pytheos = pytheos.Pytheos('127.0.0.1', 1255)
        self._pytheos.api.send_command = unittest.mock.MagicMock()

    def test_command_failure(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('system', 'register_for_change_events', 'fail')):
            with self.assertRaises(CommandFailedError):
                _async_run(self._pytheos.api.system.register_for_change_events(True))

    def test_system_register_for_change_events(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('system', 'register_for_change_events', 'success',
                                                                   enable='on')):
            _async_run(self._pytheos.api.system.register_for_change_events(True))
            self._pytheos.api.send_command.assert_called_with('system', 'register_for_change_events', enable='on')

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('system', 'register_for_change_events', 'success',
                                                                   enable='off')):
            _async_run(self._pytheos.api.system.register_for_change_events(False))
            self._pytheos.api.send_command.assert_called_with('system', 'register_for_change_events', enable='off')

    def test_system_check_account(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('system', 'check_account', 'success',
                                                                   message=f"signed_in&un={TEST_EMAIL}")):
            status, email = _async_run(self._pytheos.api.system.check_account())
            self.assertEqual(status, AccountStatus.SignedIn)
            self.assertEqual(email, TEST_EMAIL)
            self._pytheos.api.send_command.assert_called_with('system', 'check_account')

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('system', 'check_account', 'success',
                                                                   message=f"signed_out")):
            status, email = _async_run(self._pytheos.api.system.check_account())
            self.assertEqual(status, AccountStatus.SignedOut)
            self.assertIsNone(email)
            self._pytheos.api.send_command.assert_called_with('system', 'check_account')

    def test_system_sign_in(self):
        password = 'somepassword'

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('system', 'sign_in', 'success',
                                                                   message=f"signed_in&un={TEST_EMAIL}")):
            _async_run(self._pytheos.api.system.sign_in(TEST_EMAIL, password))
            self._pytheos.api.send_command.assert_called_with('system', 'sign_in', un=TEST_EMAIL, pw=password)

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('system', 'sign_in', 'fail')):
            with self.assertRaises(SignInFailedError):
                _async_run(self._pytheos.api.system.sign_in(TEST_EMAIL, password))

    def test_system_sign_out(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('system', 'sign_out', 'success', message='signed_out')):
            _async_run(self._pytheos.api.system.sign_out())
            self._pytheos.api.send_command.assert_called_with('system', 'sign_out')

    def test_system_heart_beat(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('system', 'heart_beat', 'success')):
            _async_run(self._pytheos.api.system.heart_beat())
            self._pytheos.api.send_command.assert_called_with('system', 'heart_beat')

    def test_system_reboot(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=None):
            _async_run(self._pytheos.api.system.reboot())
            self._pytheos.api.send_command.assert_called_with('system', 'reboot')

    def test_system_prettify_json_response(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('system', 'prettify_json_response', 'success', enable='on')):
            _async_run(self._pytheos.api.system.prettify_json_response(True))
            self._pytheos.api.send_command.assert_called_with('system', 'prettify_json_response', enable='on')

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('system', 'prettify_json_response', 'success', enable='off')):
            _async_run(self._pytheos.api.system.prettify_json_response(False))
            self._pytheos.api.send_command.assert_called_with('system', 'prettify_json_response', enable='off')

    def test_player_get_players(self):
        response = TestAPIs.get_basic_response('player', 'get_players', 'success')
        response['payload'] = [
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

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            players = _async_run(self._pytheos.api.player.get_players())
            self.assertGreater(len(players), 0)
            self.assertIsInstance(players[0], Player)

    def test_player_get_player_info(self):
        response = TestAPIs.get_basic_response('player', 'get_player_info', 'success')
        response['payload'] = {
            "name": "Marantz PM7000N",
            "pid": TEST_PLAYER_ID,
            "model": "Marantz PM7000N",
            "version": "1.562.230",
            "ip": "10.10.0.7",
            "network": "wifi",
            "lineout": 0,
            "serial": "SN12345678"
        }

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            result = _async_run(self._pytheos.api.player.get_player_info(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'get_player_info', pid=TEST_PLAYER_ID)
            self.assertIsInstance(result, Player)

    def test_player_get_play_state(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'get_play_state', 'success',
                                                                   pid=TEST_PLAYER_ID, state='stop')):
            play_state = _async_run(self._pytheos.api.player.get_play_state(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'get_play_state', pid=TEST_PLAYER_ID)
            self.assertEqual(play_state, PlayState.Stopped)

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'get_play_state', 'success',
                                                                   pid=TEST_PLAYER_ID, state='play')):
            play_state = _async_run(self._pytheos.api.player.get_play_state(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'get_play_state', pid=TEST_PLAYER_ID)
            self.assertEqual(play_state, PlayState.Playing)

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'get_play_state', 'success',
                                                                   pid=TEST_PLAYER_ID, state='pause')):
            play_state = _async_run(self._pytheos.api.player.get_play_state(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'get_play_state', pid=TEST_PLAYER_ID)
            self.assertEqual(play_state, PlayState.Paused)

    def test_player_set_play_state(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'set_play_state', 'success',
                                                                   pid=TEST_PLAYER_ID, state='stop')):
            _async_run(self._pytheos.api.player.set_play_state(TEST_PLAYER_ID, PlayState.Stopped))
            self._pytheos.api.send_command.assert_called_with('player', 'set_play_state', pid=TEST_PLAYER_ID, state=PlayState.Stopped)

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'set_play_state', 'success',
                                                                   pid=TEST_PLAYER_ID, state='play')):
            _async_run(self._pytheos.api.player.set_play_state(TEST_PLAYER_ID, PlayState.Playing))
            self._pytheos.api.send_command.assert_called_with('player', 'set_play_state', pid=TEST_PLAYER_ID, state=PlayState.Playing)

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'set_play_state', 'success',
                                                                   pid=TEST_PLAYER_ID, state='pause')):
            _async_run(self._pytheos.api.player.set_play_state(TEST_PLAYER_ID, PlayState.Paused))
            self._pytheos.api.send_command.assert_called_with('player', 'set_play_state', pid=TEST_PLAYER_ID, state=PlayState.Paused)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.set_play_state(TEST_PLAYER_ID, 'invalid_state'))

    def test_player_get_now_playing_media(self):
        response = TestAPIs.get_basic_response('player', 'get_now_playing_media', 'success', pid=TEST_PLAYER_ID)
        response['payload'] = {
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
        }
        response['options'] = [
            {
                "play": [
                    {"id": 11, "name": "Thumbs Up"},
                    {"id": 12, "name": "Thumbs Down"},
                    {"id": 19, "name": "Add to HEOS Favorites"}
                ]
            }
        ]

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            now_playing = _async_run(self._pytheos.api.player.get_now_playing_media(TEST_PLAYER_ID))    # FIXME?: What about the options?
            self._pytheos.api.send_command.assert_called_with('player', 'get_now_playing_media', pid=TEST_PLAYER_ID)
            self.assertIsInstance(now_playing, MediaItem)

    def test_player_get_volume(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'get_volume', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   level=10)):
            volume = _async_run(self._pytheos.api.player.get_volume(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'get_volume', pid=TEST_PLAYER_ID)
            self.assertEqual(volume, 10)

    def test_player_set_volume(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'set_volume', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   level=20)):
            _async_run(self._pytheos.api.player.set_volume(TEST_PLAYER_ID, 20))
            self._pytheos.api.send_command.assert_called_with('player', 'set_volume', pid=TEST_PLAYER_ID, level=20)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.set_volume(TEST_PLAYER_ID, 101))
        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.set_volume(TEST_PLAYER_ID, -1))

    def test_player_volume_up(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'volume_up', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   step=5)):
            _async_run(self._pytheos.api.player.volume_up(TEST_PLAYER_ID, 5))
            self._pytheos.api.send_command.assert_called_with('player', 'volume_up', pid=TEST_PLAYER_ID, step=5)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.volume_up(TEST_PLAYER_ID, 11))
        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.volume_up(TEST_PLAYER_ID, 0))

    def test_player_volume_down(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'volume_down', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   step=5)):
            _async_run(self._pytheos.api.player.volume_down(TEST_PLAYER_ID, 5))
            self._pytheos.api.send_command.assert_called_with('player', 'volume_down', pid=TEST_PLAYER_ID, step=5)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.volume_down(TEST_PLAYER_ID, 11))
        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.volume_down(TEST_PLAYER_ID, 0))

    def test_player_get_mute(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'get_mute', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   state='off')):
            muted = _async_run(self._pytheos.api.player.get_mute(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'get_mute', pid=TEST_PLAYER_ID)
            self.assertEqual(muted, False)

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'get_mute', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   state='on')):
            muted = _async_run(self._pytheos.api.player.get_mute(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'get_mute', pid=TEST_PLAYER_ID)
            self.assertEqual(muted, True)

    def test_player_set_mute(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'set_mute', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   state='on')):
            _async_run(self._pytheos.api.player.set_mute(TEST_PLAYER_ID, True))
            self._pytheos.api.send_command.assert_called_with('player', 'set_mute', pid=TEST_PLAYER_ID, state=Mute.On)

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'set_mute', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   state='off')):
            _async_run(self._pytheos.api.player.set_mute(TEST_PLAYER_ID, False))
            self._pytheos.api.send_command.assert_called_with('player', 'set_mute', pid=TEST_PLAYER_ID, state=Mute.Off)

    def test_player_toggle_mute(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'get_mute', 'success',
                                                                   pid=TEST_PLAYER_ID)):
            _async_run(self._pytheos.api.player.toggle_mute(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'toggle_mute', pid=TEST_PLAYER_ID)

    def test_player_get_play_mode(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'get_play_mode', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   repeat='off',
                                                                   shuffle='off')):
            play_mode = _async_run(self._pytheos.api.player.get_play_mode(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'get_play_mode', pid=TEST_PLAYER_ID)
            self.assertIsInstance(play_mode, PlayMode)
            self.assertEqual(play_mode.repeat, RepeatMode.Off)
            self.assertEqual(play_mode.shuffle, ShuffleMode.Off)

    def test_player_set_play_mode(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'set_play_mode', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   repeat='off',
                                                                   shuffle='off')):
            _async_run(self._pytheos.api.player.set_play_mode(TEST_PLAYER_ID, PlayMode(repeat=RepeatMode.Off, shuffle=ShuffleMode.Off)))
            self._pytheos.api.send_command.assert_called_with('player', 'set_play_mode', pid=TEST_PLAYER_ID, repeat=RepeatMode.Off, shuffle=ShuffleMode.Off)

    def test_player_get_queue(self):
        start_pos = 0
        retrieve_count = 10

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=TestAPIs.get_demo_queue()):
            queue = _async_run(self._pytheos.api.player.get_queue(TEST_PLAYER_ID, start_pos, retrieve_count))
            self._pytheos.api.send_command.assert_called_with('player', 'get_queue',
                                                              pid=TEST_PLAYER_ID,
                                                              range=','.join((str(start_pos), str(retrieve_count - 1))))
            self.assertIsInstance(queue, list)
            self.assertGreater(len(queue), 0)
            self.assertIsInstance(queue[0], MediaItem)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.get_queue(TEST_PLAYER_ID, -1, 10))  # Lower limit too small
        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.get_queue(TEST_PLAYER_ID, 0, 101))  # Number to retrieve too large
        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.get_queue(TEST_PLAYER_ID, 0, 0))    # Number to retrieve too small

    def test_player_play_queue(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=TestAPIs.get_demo_queue()):
            queue = _async_run(self._pytheos.api.player.get_queue(TEST_PLAYER_ID, 0, 10))

            _async_run(self._pytheos.api.player.play_queue(TEST_PLAYER_ID, queue[0].queue_id))
            self._pytheos.api.send_command.assert_called_with('player', 'play_queue', pid=TEST_PLAYER_ID, qid=queue[0].queue_id)

    def test_player_remove_from_queue(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'remove_from_queue', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   qid=0)):
            _async_run(self._pytheos.api.player.remove_from_queue(TEST_PLAYER_ID, queue_ids=(0,)))
            self._pytheos.api.send_command.assert_called_with('player', 'remove_from_queue', pid=TEST_PLAYER_ID, qid='0')

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'remove_from_queue', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   qid='0,1')):
            _async_run(self._pytheos.api.player.remove_from_queue(TEST_PLAYER_ID, queue_ids=(0, 1)))
            self._pytheos.api.send_command.assert_called_with('player', 'remove_from_queue', pid=TEST_PLAYER_ID, qid='0,1')

    def test_player_save_queue(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'save_queue', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   name='Test Playlist')):
            _async_run(self._pytheos.api.player.save_queue(TEST_PLAYER_ID, "Test Playlist"))
            self._pytheos.api.send_command.assert_called_with('player', 'save_queue',
                                                              pid=TEST_PLAYER_ID, name='Test Playlist')

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.save_queue(TEST_PLAYER_ID, '*'*129))     # Name too long

    def test_player_clear_queue(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'clear_queue', 'success', pid=TEST_PLAYER_ID)):
            _async_run(self._pytheos.api.player.clear_queue(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'clear_queue', pid=TEST_PLAYER_ID)

    def test_player_move_queue_item(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'move_queue_item', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   sqid=1,
                                                                   dqid=1)):
            _async_run(self._pytheos.api.player.move_queue_item(TEST_PLAYER_ID, queue_ids=(1,), destination_queue_id=1))
            self._pytheos.api.send_command.assert_called_with('player', 'move_queue_item', pid=TEST_PLAYER_ID, sqid='1', dqid=1)

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'move_queue_item', 'success',
                                                                   pid=TEST_PLAYER_ID,
                                                                   sqid='1,2',
                                                                   dqid=3)):
            _async_run(self._pytheos.api.player.move_queue_item(TEST_PLAYER_ID, queue_ids=(1, 2), destination_queue_id=3))
            self._pytheos.api.send_command.assert_called_with('player', 'move_queue_item', pid=TEST_PLAYER_ID, sqid='1,2', dqid=3)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.move_queue_item(TEST_PLAYER_ID, queue_ids=(1,), destination_queue_id=0))  # Invalid destination ID
        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.move_queue_item(TEST_PLAYER_ID, queue_ids=(0,), destination_queue_id=4))  # Invalid source ID

    def test_player_play_next(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'play_next', 'success',
                                                                   pid=TEST_PLAYER_ID)):
            _async_run(self._pytheos.api.player.play_next(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'play_next', pid=TEST_PLAYER_ID)

    def test_player_play_previous(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'play_previous', 'success',
                                                                   pid=TEST_PLAYER_ID)):
            _async_run(self._pytheos.api.player.play_previous(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'play_previous', pid=TEST_PLAYER_ID)

    def test_player_set_quickselect(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'set_quickselect', 'success',
                                                                   pid=TEST_PLAYER_ID, id=1)):
            _async_run(self._pytheos.api.player.set_quickselect(TEST_PLAYER_ID, 1))
            self._pytheos.api.send_command.assert_called_with('player', 'set_quickselect', pid=TEST_PLAYER_ID, id=1)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.set_quickselect(TEST_PLAYER_ID, 0))  # Value too small
        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.set_quickselect(TEST_PLAYER_ID, 7))  # Value too large

    def test_player_play_quickselect(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('player', 'play_quickselect', 'success',
                                                                   pid=TEST_PLAYER_ID, id=1)):
            _async_run(self._pytheos.api.player.play_quickselect(TEST_PLAYER_ID, 1))
            self._pytheos.api.send_command.assert_called_with('player', 'play_quickselect', pid=TEST_PLAYER_ID, id=1)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.play_quickselect(TEST_PLAYER_ID, 0))     # Value too small
        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.player.play_quickselect(TEST_PLAYER_ID, 7))     # Value too large

    def test_player_get_quickselects(self):
        response = TestAPIs.get_basic_response('player', 'get_quickselects', 'success', pid=TEST_PLAYER_ID)
        response['payload'] = [
            {'id': 1, 'name': 'Quick Select 1'},
            {'id': 2, 'name': 'Quick Select 2'},
            {'id': 3, 'name': 'Quick Select 3'},
        ]

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            quick_selects = _async_run(self._pytheos.api.player.get_quickselects(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'get_quickselects', pid=TEST_PLAYER_ID)

            self.assertIsInstance(quick_selects, list)
            self.assertGreater(len(quick_selects), 0)
            self.assertIsInstance(quick_selects[0], QuickSelect)

    def test_player_check_update(self):
        response = TestAPIs.get_basic_response('player', 'check_update', 'success', pid=TEST_PLAYER_ID)
        response['payload'] = {'update': 'update_none'}

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            update_available = _async_run(self._pytheos.api.player.check_update(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'check_update', pid=TEST_PLAYER_ID)
            self.assertEqual(update_available, False)

        response['payload'] = {'update': 'update_exist'}
        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            update_available = _async_run(self._pytheos.api.player.check_update(TEST_PLAYER_ID))
            self._pytheos.api.send_command.assert_called_with('player', 'check_update', pid=TEST_PLAYER_ID)
            self.assertEqual(update_available, True)

    def test_group_get_groups(self):
        response = TestAPIs.get_basic_response('group', 'get_groups', 'success')
        response['payload'] = [
            {
                "name": "group name 1",
                "gid": "group id 1",
                "players": [
                    {
                        "name": "player name 1",
                        "pid": "player id 1",
                        "role": "leader",
                    },
                    {
                        "name": "player name 2",
                        "pid": "player id 2",
                        "role": "member",
                    },
                    {
                        "name": "player name 3",
                        "pid": "player id 3",
                        "role": "member",
                    }
                ]
            },
            {
                "name": "group name 2",
                "gid": "group id 2",
                "players": [
                    {
                        "name": "player name 3",
                        "pid": "player id 4",
                        "role": "member",
                    },
                    {
                        "name": "player name 4",
                        "pid": "player id 4",
                        "role": "member",
                    },
                    {
                        "name": "player name 5",
                        "pid": "player id 5",
                        "role": "leader",
                    }
                ]
            },
        ]

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            groups = _async_run(self._pytheos.api.group.get_groups())
            self._pytheos.api.send_command.assert_called_with('group', 'get_groups')
            self.assertEqual(len(groups), 2)
            self.assertIsInstance(groups[0], Group)
            self.assertIsInstance(groups[0].players[0], GroupPlayer)
            self.assertIsInstance(groups[0].players[0].role, GroupRole)

    def test_group_get_group_info(self):
        response = TestAPIs.get_basic_response('group', 'get_group_info', 'success', gid=TEST_GROUP_ID)
        response['payload'] = {
            "name": "group name 1",
            "gid": f"{TEST_GROUP_ID}",
            "players": [
                {
                    "name": "player name 1",
                    "pid": "player id 1",
                    "role": "leader",
                },
                {
                    "name": "player name 2",
                    "pid": "player id 2",
                    "role": "member",
                },
                {
                    "name": "player name 3",
                    "pid": "player id 3",
                    "role": "member",
                }
            ]
        }
        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            group_info = _async_run(self._pytheos.api.group.get_group_info(TEST_GROUP_ID))
            self._pytheos.api.send_command.assert_called_with('group', 'get_group_info', gid=TEST_GROUP_ID)
            self.assertIsInstance(group_info, Group)

    def test_group_set_group(self):
        leader = 1
        members = [2, 3]

        # Create/modify group
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('group', 'set_group', 'success',
                                                                   gid='1',
                                                                   name='Group 1',
                                                                   pid=','.join(str(n) for n in [leader]+members))):
            results = _async_run(self._pytheos.api.group.set_group(leader, members))
            self._pytheos.api.send_command.assert_called_with('group', 'set_group', pid=','.join(str(n) for n in [leader]+members))
            self.assertIsInstance(results, Group)

        # Ungroup all
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('group', 'set_group', 'success', pid=leader)):
            results = _async_run(self._pytheos.api.group.set_group(leader))
            self._pytheos.api.send_command.assert_called_with('group', 'set_group', pid=str(leader))
            self.assertIsNone(results)

    def test_group_get_volume(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('group', 'get_volume', 'success',
                                                                   gid=TEST_GROUP_ID,
                                                                   level=50)):
            volume = _async_run(self._pytheos.api.group.get_volume(TEST_GROUP_ID))
            self._pytheos.api.send_command.assert_called_with('group', 'get_volume', gid=TEST_GROUP_ID)
            self.assertIsInstance(volume, int)
            self.assertTrue(0 <= volume <= 100)

    def test_group_set_volume(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('group', 'set_volume', 'success',
                                                                   gid=TEST_GROUP_ID,
                                                                   level=20)):
            _async_run(self._pytheos.api.group.set_volume(TEST_GROUP_ID, 20))
            self._pytheos.api.send_command.assert_called_with('group', 'set_volume', gid=TEST_GROUP_ID, level=20)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.group.set_volume(TEST_GROUP_ID, 101))
        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.group.set_volume(TEST_GROUP_ID, -1))

    def test_group_volume_up(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('group', 'volume_up', 'success',
                                                                   gid=TEST_GROUP_ID,
                                                                   step=5)):
            _async_run(self._pytheos.api.group.volume_up(TEST_GROUP_ID, 5))
            self._pytheos.api.send_command.assert_called_with('group', 'volume_up', gid=TEST_GROUP_ID, step=5)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.group.volume_up(TEST_GROUP_ID, 11))
        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.group.volume_up(TEST_GROUP_ID, 0))

    def test_group_volume_down(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('group', 'volume_down', 'success',
                                                                   gid=TEST_GROUP_ID,
                                                                   step=5)):
            _async_run(self._pytheos.api.group.volume_down(TEST_GROUP_ID, 5))
            self._pytheos.api.send_command.assert_called_with('group', 'volume_down', gid=TEST_GROUP_ID, step=5)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.group.volume_down(TEST_GROUP_ID, 11))
        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.group.volume_down(TEST_GROUP_ID, 0))

    def test_group_get_mute(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('group', 'get_mute', 'success',
                                                                   gid=TEST_GROUP_ID,
                                                                   state='on')):
            muted = _async_run(self._pytheos.api.group.get_mute(TEST_GROUP_ID))
            self._pytheos.api.send_command.assert_called_with('group', 'get_mute', gid=TEST_GROUP_ID)
            self.assertEqual(muted, True)

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('group', 'get_mute', 'success',
                                                                   gid=TEST_GROUP_ID,
                                                                   state='off')):
            muted = _async_run(self._pytheos.api.group.get_mute(TEST_GROUP_ID))
            self._pytheos.api.send_command.assert_called_with('group', 'get_mute', gid=TEST_GROUP_ID)
            self.assertEqual(muted, False)

    def test_group_set_mute(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('group', 'set_mute', 'success',
                                                                   gid=TEST_GROUP_ID,
                                                                   state='on')):
            _async_run(self._pytheos.api.group.set_mute(TEST_GROUP_ID, True))
            self._pytheos.api.send_command.assert_called_with('group', 'set_mute', gid=TEST_GROUP_ID, state=Mute.On)

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('group', 'set_mute', 'success',
                                                                   gid=TEST_GROUP_ID,
                                                                   state='off')):
            _async_run(self._pytheos.api.group.set_mute(TEST_GROUP_ID, False))
            self._pytheos.api.send_command.assert_called_with('group', 'set_mute', gid=TEST_GROUP_ID, state=Mute.Off)

    def test_group_toggle_mute(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('group', 'toggle_mute', 'success')):
            _async_run(self._pytheos.api.group.toggle_mute(TEST_GROUP_ID))
            self._pytheos.api.send_command.assert_called_with('group', 'toggle_mute', gid=TEST_GROUP_ID)

    def test_browse_get_music_sources(self):
        response = TestAPIs.get_basic_response('browse', 'get_music_sources', 'success')
        response['payload'] = [
            {
                "name": "Pandora",
                "image_url": "https://production.ws.skyegloup.com:443/media/images/service/logos/pandora.png",
                "type": "music_service",
                "sid": 1,
                "available": "true",
                "service_username": TEST_EMAIL
            },
            {
                "name": "iHeartRadio",
                "image_url": "https://production.ws.skyegloup.com:443/media/images/service/logos/iheartradio.png",
                "type": "music_service",
                "sid": 7,
                "available": "false"
            }
        ]
        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            music_sources = _async_run(self._pytheos.api.browse.get_music_sources())
            self._pytheos.api.send_command.assert_called_with('browse', 'get_music_sources')
            self.assertGreater(len(music_sources), 0)
            self.assertIsInstance(music_sources[0], Source)

    def test_browse_get_source_info(self):
        response = TestAPIs.get_basic_response('browse', 'get_music_sources', 'success')
        response['payload'] = {
            "name": "Pandora",
            "image_url": "https://production.ws.skyegloup.com:443/media/images/service/logos/pandora.png",
            "type": "music_service",
            "sid": 1,
            "available": "true",
            "service_username": TEST_EMAIL
        }

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            self.assertIsInstance(_async_run(self._pytheos.api.browse.get_source_info(1)), Source)
            self._pytheos.api.send_command.assert_called_with('browse', 'get_source_info', sid=1)

    def test_browse_browse_source(self):
        response = TestAPIs.get_basic_response('browse', 'browse', 'success', sid=1, returned=2, count=2)
        response['payload'] = [
            {
                "container": "yes",
                "playable": "no",
                "type": "container",
                "name": "By Date",
                "image_uri": "",
                "image_url": "",
                "cid": "By Date"
            },
            {
                "container": "yes",
                "playable": "no",
                "type": "container",
                "name": "A-Z",
                "image_uri": "",
                "image_url": "",
                "cid": "A-Z"
            }
        ]

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            results = _async_run(self._pytheos.api.browse.browse_source(1))
            self._pytheos.api.send_command.assert_called_with('browse', 'browse', sid=1)
            self.assertGreater(len(results), 0)
            self.assertIsInstance(results[0], Source)

    def test_browse_browse_source_container(self):
        source_id = 1340337940
        container_id = 'abe6121c-1731-4683-815c-89e1dcd2bf11'

        response = TestAPIs.get_basic_response('browse', 'browse', 'success', sid=source_id, cid=container_id, returned=1, count=1)
        response['payload'] = [
            {
                "container": "yes",
                "type": "artist",
                "cid": "4c07e4537a6772cb2675",
                "playable": "no",
                "name": "Music",
                "image_url": ""
            }
        ]

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            results = _async_run(self._pytheos.api.browse.browse_source_container(source_id, container_id))
            self._pytheos.api.send_command.assert_called_with('browse', 'browse', sid=source_id, cid=container_id)
            self.assertGreater(len(results), 0)
            self.assertIsInstance(results[0], Source)

    def test_browse_get_search_criteria(self):
        sid = 1340337940

        response = TestAPIs.get_basic_response('browse', 'get_search_criteria', 'success', sid=sid)
        response['payload'] = [
            {
                "name": "Artist",
                "scid": 1,
                "wildcard": "no"
            },
            {
                "name": "Album",
                "scid": 2,
                "wildcard": "no"
            },
            {
                "name": "Track",
                "scid": 3,
                "wildcard": "no",
                "cid": "SEARCHED_TRACKS-",
                "playable": "yes"
            }
        ]

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            results = _async_run(self._pytheos.api.browse.get_search_criteria(sid))
            self._pytheos.api.send_command.assert_called_with('browse', 'get_search_criteria', sid=sid)
            self.assertGreater(len(results), 0)
            self.assertIsInstance(results[0], SearchCriteria)

    def test_browse_search(self):
        sid = 1340337940

        response = TestAPIs.get_basic_response('browse', 'search', 'success',
                                               sid=sid, search='someband', scid=1,
                                               returned=3, count=3)
        response['payload'] = [
            {
                "container": "no",
                "mid": "CREATE_STATION-S10198430",
                "type": "station",
                "playable": "yes",
                "name": "Some Bands (Feat. Mozzy) by Murdah 1",
                "image_url": ""
            },
            {
                "container": "no",
                "mid": "CREATE_STATION-S12797360",
                "type": "station",
                "playable": "yes",
                "name": "The One I Love Belongs To Somebod by Frank Sinatra %26 Tommy Dorsey",
                "image_url": ""
            },
            {
                "container": "no",
                "mid": "CREATE_STATION-S29863954",
                "type": "station",
                "playable": "yes",
                "name": "Some Bands Have All the Fun by The Easy Button",
                "image_url": ""
            }
        ]

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            results = _async_run(self._pytheos.api.browse.search(sid, 'someband', 1))
            self._pytheos.api.send_command.assert_called_with('browse', 'search', sid=sid, search='someband', scid=1)
            self.assertGreater(len(results), 0)
            self.assertIsInstance(results[0], Source)

    def test_browse_play_station(self):
        pid = 12345678
        sid = 1
        cid = 'A-Z'
        mid = 1156081746731893318
        name = 'Shuffle'

        response = TestAPIs.get_basic_response('browse', 'play_stream', 'success',
                                               pid=pid, sid=sid, cid=cid, mid=mid, name=name)

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            _async_run(self._pytheos.api.browse.play_station(pid, sid, cid, mid, name))
            self._pytheos.api.send_command.assert_called_with('browse', 'play_stream', pid=pid, sid=sid, cid=cid, mid=mid, name=name)

    def test_browse_play_preset(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('browse', 'play_preset', 'success',
                                                                   pid=TEST_PLAYER_ID, preset=1)):
            _async_run(self._pytheos.api.browse.play_preset(TEST_PLAYER_ID, 1))
            self._pytheos.api.send_command.assert_called_with('browse', 'play_preset', pid=TEST_PLAYER_ID, preset=1)

        with self.assertRaises(ValueError):
            _async_run(self._pytheos.api.browse.play_preset(TEST_PLAYER_ID, 0))

    def test_browse_play_input(self):
        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('browse', 'play_input', 'success',
                                                                   pid=TEST_PLAYER_ID, input=str(InputSource.Phono))):
            _async_run(self._pytheos.api.browse.play_input(TEST_PLAYER_ID, InputSource.Phono))
            self._pytheos.api.send_command.assert_called_with('browse', 'play_input', pid=TEST_PLAYER_ID, input=InputSource.Phono)

    def test_browse_play_url(self):
        url = 'http://someserver/somestream.mp3'

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('browse', 'play_url', 'success',
                                                                   pid=TEST_PLAYER_ID, url=url)):
            _async_run(self._pytheos.api.browse.play_url(TEST_PLAYER_ID, url))

    def test_browse_add_container_to_queue(self):
        sid = 1340337940
        cid = 'd4d42d93deb97cb2db7b'

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('browse', 'add_to_queue', 'success',
                                                                   pid=TEST_PLAYER_ID, sid=sid, cid=cid, aid=3)):
            _async_run(self._pytheos.api.browse.add_to_queue(TEST_PLAYER_ID, sid, cid, add_type=AddToQueueType.AddToEnd))
            self._pytheos.api.send_command.assert_called_with('browse', 'add_to_queue', pid=TEST_PLAYER_ID,
                                                              sid=sid, cid=cid, aid=AddToQueueType.AddToEnd)

    def test_browse_add_track_to_queue(self):
        sid = 1340337940
        cid = '8eb5b733259c7a9fea25'
        mid = '36fad30531d3e5bceec6'

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('browse', 'add_to_queue', 'success',
                                                                   pid=TEST_PLAYER_ID, sid=sid, cid=cid, mid=mid, aid=3)):
            _async_run(self._pytheos.api.browse.add_to_queue(TEST_PLAYER_ID, sid, cid, media_id=mid, add_type=AddToQueueType.AddToEnd))
            self._pytheos.api.send_command.assert_called_with('browse', 'add_to_queue', pid=TEST_PLAYER_ID,
                                                              sid=sid, cid=cid, mid=mid, aid=AddToQueueType.AddToEnd)

    def test_browse_rename_playlist(self):
        sid = 1025
        cid = 259539
        name = 'foobar'

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('browse', 'rename_playlist', 'success',
                                                                   sid=sid, cid=cid, name=name)):
            _async_run(self._pytheos.api.browse.rename_playlist(sid, cid, name))
            self._pytheos.api.send_command.assert_called_with('browse', 'rename_playlist', sid=sid, cid=cid, name=name)

    def test_browse_delete_playlist(self):
        sid = 1025
        cid = 259539

        with patch.object(pytheos.networking.connection.Connection, 'read_message',
                          return_value=TestAPIs.get_basic_response('browse', 'delete_playlist', 'success',
                                                                   sid=sid, cid=cid)):
            _async_run(self._pytheos.api.browse.delete_playlist(sid, cid))
            self._pytheos.api.send_command.assert_called_with('browse', 'delete_playlist', sid=sid, cid=cid)

    def test_browse_retrieve_metadata(self):
        sid = 1
        cid = 1

        response = TestAPIs.get_basic_response('browse', 'retrieve_metadata', 'success', sid=sid, cid=cid)
        response['payload'] = [
            {
                "album_id": "1",
                "images": [
                    {
                        "image_url": "http://someserver/someimage.jpg",
                        "width": 240,
                    },
                    {
                        "image_url": "http://otherserver/someimage.jpg",
                        "width": 240,
                    },
                ]
            }
        ]

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            results = _async_run(self._pytheos.api.browse.retrieve_metadata(sid, cid))
            self._pytheos.api.send_command.assert_called_with('browse', 'retrieve_metadata', sid=sid, cid=cid)
            self.assertGreater(len(results), 0)
            self.assertIsInstance(results[0], AlbumMetadata)

    def test_browse_set_service_option(self):
        sid = 1
        query = 'foobar'

        response = TestAPIs.get_basic_response('browse', 'retrieve_metadata', 'success',
                                               sid=sid, search=query, scid=1, range='0,100',
                                               returned=2, count=2)
        response['payload'] = [
            {
                "container": "no",
                "mid": "CREATE_STATION-R297856",
                "type": "station",
                "playable": "yes",
                "name": "Finbar Furey",
                "image_url": ""
            },
            {
                "container": "no",
                "mid": "CREATE_STATION-R736713",
                "type": "station",
                "playable": "yes",
                "name": "Finbar Wright",
                "image_url": ""
            }
        ]

        with patch.object(pytheos.networking.connection.Connection, 'read_message', return_value=response):
            results = _async_run(self._pytheos.api.browse.set_service_option(sid, ServiceOption.CreateNewStation, name=query))
            self._pytheos.api.send_command.assert_called_with('browse', 'set_service_option', sid=sid, option=ServiceOption.CreateNewStation, name=query)
            self.assertGreater(int(results.header.vars.get('returned', 0)), 0)

    # Utils
    @staticmethod
    def get_demo_queue():
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

    @staticmethod
    def get_basic_response(group, command, success, message=None, **kwargs) -> Union[List, Dict]:
        return {
            "heos": {
                "command": f"{group}/{command}",
                "result": success,
                "message": message if message else '&'.join('='.join((k, str(v))) for k, v in kwargs.items())
            }
        }


if __name__ == '__main__':
    unittest.main()
