#!/usr/bin/env python
from ..api import API
from .types import Player
from ... import utils


class PlayerAPI(API):
    def get_players(self):
        header, payload = self._pytheos.api.call('player', 'get_players')

        players = []
        if header.succeeded:
            for player_data in payload:
                players.append(Player(player_data))

        return players

    def get_player_info(self, player_id):
        header, payload = self._pytheos.api.call('player', 'get_player_info', pid=player_id)

        player_info = None
        if header.succeeded:
            player_info = Player(payload)

        return player_info

    def get_play_state(self, player_id):
        header, payload = self._pytheos.api.call('player', 'get_play_state', pid=player_id)

        state = None
        if header.succeeded:
            vars = utils.parse_var_string(header.message)
            state = vars.get('state')

        return state
