#!/usr/bin/env python
""" Provides the API abstraction for the 'system' command group """

from __future__ import annotations

from .api import API
from ..errors import CommandFailedError, SignInFailedError
from ..types import AccountStatus


class SystemAPI(API):
    """ API interface for the 'system' command group """

    def check_account(self) -> tuple:
        """ Determines whether or not the system is currently signed in

        :return: (status, username)
        """
        results = self._api.call('system', 'check_account')

        username = results.header.vars.get('un')
        result = results.header.vars.get('signed_out')
        if not result:
            result = results.header.vars.get('signed_in')

        return AccountStatus(result), username

    def heart_beat(self) -> None:
        """ Executes the heart_beat command

        :return: None
        """
        self._api.call('system', 'heart_beat')

    def prettify_json_response(self, enable: bool) -> None:
        """ Enables or disables pretty JSON responses

        :param enable: True or False
        :return: None
        """
        self._api.call('system', 'prettify_json_response', enable='on' if enable else 'off')

    def reboot(self) -> None:
        """ Forces the system to reboot

        :return: None
        """
        self._api.call('system', 'reboot')

    def register_for_change_events(self, enable: bool) -> None:
        """ Registers the current connection to receive events from HEOS.

        :param enable: True or False
        :return: None
        """
        self._api.call('system', 'register_for_change_events', enable='on' if enable else 'off')

    def sign_in(self, username: str, password: str) -> None:
        """ Commands the system to signin to HEOS

        :param username: Username
        :param password: Password
        :raises: SignInFailedError
        :return: None
        """
        try:
            self._api.call('system', 'sign_in', un=username, pw=password)
        except CommandFailedError as ex:
            raise SignInFailedError('HEOS sign-in failed', ex.result) from ex

    def sign_out(self) -> None:
        """ Commands the system to sign out of HEOS.

        :return: None
        """
        self._api.call('system', 'sign_out')
