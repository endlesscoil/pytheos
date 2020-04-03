#!/usr/bin/env python
from .api import API
from .. import utils


class SystemAPI(API):
    def register_for_change_events(self, enable):
        header, payload = self._pytheos.api.call('system', 'register_for_change_events', enable='on' if enable else 'off')

        return header.succeeded

    def check_account(self):
        header, payload = self._pytheos.api.call('system', 'check_account')

        result = None
        username = None

        if header.succeeded:
            vars = utils.parse_var_string(header.message)
            username = vars.get('un')
            result = vars.get('signed_out')
            if not result:
                result = vars.get('signed_in')

        return result, username

    def sign_in(self, username, password):
        header, payload = self._pytheos.api.call('system', 'sign_in', un=username, pw=password)

        return header.succeeded

    def sign_out(self):
        header, payload = self._pytheos.api.call('system', 'sign_out')

        return header.succeeded

    def heart_beat(self):
        header, payload = self._pytheos.api.call('system', 'heart_beat')

        return header.succeeded

    def reboot(self):
        header, payload = self._pytheos.api.call('system', 'reboot')

        return header.succeeded

    def prettify_json_response(self, enable):
        header, payload = self._pytheos.api.call('system', 'prettify_json_response', enable='on' if enable else 'off')

        return header.succeeded
