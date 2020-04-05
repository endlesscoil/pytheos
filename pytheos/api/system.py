#!/usr/bin/env python
from __future__ import annotations

from .api import API
from ..errors import CommandFailedError, SignInFailedError


class SystemAPI(API):
    def check_account(self):
        results = self._pytheos.api.call('system', 'check_account')

        username = results.message_vars.get('un')
        result = results.message_vars.get('signed_out')
        if not result:
            result = results.message_vars.get('signed_in')

        return result, username

    def heart_beat(self):
        self._pytheos.api.call('system', 'heart_beat')

    def prettify_json_response(self, enable):
        self._pytheos.api.call('system', 'prettify_json_response', enable='on' if enable else 'off')

    def reboot(self):
        self._pytheos.api.call('system', 'reboot')

    def register_for_change_events(self, enable):
        self._pytheos.api.call('system', 'register_for_change_events', enable='on' if enable else 'off')

    def sign_in(self, username, password):
        try:
            self._pytheos.api.call('system', 'sign_in', un=username, pw=password)
        except CommandFailedError as ex:
            raise SignInFailedError('HEOS sign-in failed', ex.result) from ex

    def sign_out(self):
        self._pytheos.api.call('system', 'sign_out')
