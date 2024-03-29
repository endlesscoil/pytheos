#!/usr/bin/env python
""" Provides the API abstraction for the 'system' command group """

from __future__ import annotations

from ..networking.errors import CommandFailedError, SignInFailedError
from ..models.system import AccountStatus


class SystemAPI:
    """ API interface for the 'system' command group """

    def __init__(self, conn):
        self._api = conn

    async def check_account(self) -> tuple:
        """ Determines whether or not the system is currently signed in

        :return: (status, username)
        """
        results = await self._api.call('system', 'check_account')

        username = results.header.vars.get('un')
        result = results.header.vars.get('signed_out')
        if not result:
            result = results.header.vars.get('signed_in')

        return AccountStatus(result), username

    async def heart_beat(self) -> None:
        """ Executes the heart_beat command

        :return: None
        """
        await self._api.call('system', 'heart_beat')

    async def prettify_json_response(self, enable: bool) -> None:
        """ Enables or disables pretty JSON responses

        :param enable: True or False
        :return: None
        """
        await self._api.call('system', 'prettify_json_response', enable='on' if enable else 'off')

    async def reboot(self) -> None:
        """ Forces the system to reboot

        :return: None
        """
        await self._api.call('system', 'reboot')

    async def register_for_change_events(self, enable: bool) -> None:
        """ Registers the current connection to receive events from HEOS.

        :param enable: True or False
        :return: None
        """
        await self._api.call('system', 'register_for_change_events', enable='on' if enable else 'off')

    async def sign_in(self, username: str, password: str) -> None:
        """ Commands the system to sign-in to HEOS

        :param username: Username
        :param password: Password
        :raises: SignInFailedError
        :return: None
        """
        try:
            await self._api.call('system', 'sign_in', un=username, pw=password)
        except CommandFailedError as ex:
            raise SignInFailedError('HEOS sign-in failed', ex.result) from ex

    async def sign_out(self) -> None:
        """ Commands the system to sign out of HEOS.

        :return: None
        """
        await self._api.call('system', 'sign_out')
