#!/usr/bin/env python
from __future__ import annotations

import os
import sys

from pytheos.api.browse.browse import BrowseAPI
from pytheos.api.browse.types import MusicSource
from pytheos.api.group.group import GroupAPI
from pytheos.api.group.types import Group
from pytheos.api.player.player import PlayerAPI
from pytheos.api.player.types import Player
from pytheos.errors import SignInFailedError
from pytheos.group import PytheosGroup
from pytheos.player import PytheosPlayer
from pytheos.source import PytheosSource
from pytheos.types import AccountStatus

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..")) # FIXME

import unittest
import unittest.mock
from unittest.mock import patch
import pytheos
from pytheos.api.system import SystemAPI


class TestPytheos(unittest.TestCase):
    TEST_EMAIL = 'username@someemailplace.com'

    def setUp(self) -> None:
        self._pytheos = pytheos.Pytheos('127.0.0.1', 1255)
        self._pytheos.api.send_command = unittest.mock.MagicMock()

    def test_connect(self):
        self.fail('FIXME - figure out how to mock this.')

        server = '10.10.0.7:1255'

        with pytheos.connect(server) as connection:
            self.assertIsNotNone(connection)

    def test_refresh(self):
        self.fail('FIXME - figure out how to mock this after refresh is finished.')

        self._pytheos.refresh()

    def test_check_account(self):
        with patch.object(SystemAPI, 'check_account', return_value=(AccountStatus.SignedIn, self.TEST_EMAIL)):
            status, username = self._pytheos.check_account()
            self._pytheos.api.system.check_account.assert_called()
            self.assertEqual(status, AccountStatus.SignedIn)
            self.assertEqual(username, self.TEST_EMAIL)

        with patch.object(SystemAPI, 'check_account', return_value=(AccountStatus.SignedOut, None)):
            status, username = self._pytheos.check_account()
            self._pytheos.api.system.check_account.assert_called()
            self.assertEqual(status, AccountStatus.SignedOut)
            self.assertIsNone(username)

    def test_sign_in(self):
        with patch.object(SystemAPI, 'sign_in', side_effect=SignInFailedError('HEOS sign-in failed', None)):
            self.assertRaises(SignInFailedError, self._pytheos.sign_in, 'username', 'password')
            self._pytheos.api.system.sign_in.assert_called()

        with patch.object(SystemAPI, 'sign_in'):
            self._pytheos.sign_in('username', 'password')
            self._pytheos.api.system.sign_in.assert_called()

    def test_sign_out(self):
        with patch.object(SystemAPI, 'sign_out'):
            self._pytheos.sign_out()
            self._pytheos.api.system.sign_out.assert_called()

    def test_get_players(self):
        with patch.object(PlayerAPI, 'get_players', return_value=[Player(), Player()]):
            players = self._pytheos.get_players()
            self.assertGreater(len(players), 0)
            self.assertIsInstance(players[0], PytheosPlayer)

    def test_get_groups(self):
        with patch.object(GroupAPI, 'get_groups', return_value=[Group(), Group()]):
            groups = self._pytheos.get_groups()
            self.assertGreater(len(groups), 0)
            self.assertIsInstance(groups[0], PytheosGroup)

    def test_get_sources(self):
        with patch.object(BrowseAPI, 'get_music_sources', return_value=[MusicSource(), MusicSource()]):
            groups = self._pytheos.get_sources()
            self.assertGreater(len(groups), 0)
            self.assertIsInstance(groups[0], PytheosSource)

if __name__== '__main__':
    unittest.main()
