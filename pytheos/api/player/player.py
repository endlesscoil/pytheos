#!/usr/bin/env python
from ..api import API
from .types import Player, QueueItem
from ... import utils


class PlayerAPI(API):
    def check_update(self, player_id):
        header, payload = self._pytheos.api.call('player', 'check_update', pid=player_id)

        update = None
        if payload:
            update = payload.get('update')

        return update == 'update_exist'

    def clear_queue(self, player_id):
        header, payload = self._pytheos.api.call('player', 'clear_queue', pid=player_id)
        return header.succeeded

    def get_mute(self, player_id):
        header, payload = self._pytheos.api.call('player', 'get_mute', pid=player_id)

        muted = None
        if header.succeeded:
            vars = utils.parse_var_string(header.message)
            muted = vars.get('state')

        return muted == 'on'

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

    def get_queue(self, player_id, range_start, range_end):
        header, payload = self._pytheos.api.call('player', 'get_queue', pid=player_id, range=f'{range_start},{range_end}')

        queue = []
        if header.succeeded:
            for entry in payload:
                queue.append(QueueItem(from_dict=entry))

        return queue

    def get_volume(self, player_id):
        header, payload = self._pytheos.api.call('player', 'get_volume', pid=player_id)

        volume = None
        if header.succeeded:
            vars = utils.parse_var_string(header.message)
            volume = vars.get('level')

        return int(volume) if volume is not None else None

    def play_next(self, player_id):
        header, payload = self._pytheos.api.call('player', 'play_next', pid=player_id)
        return header.succeeded

    def play_previous(self, player_id):
        header, payload = self._pytheos.api.call('player', 'play_previous', pid=player_id)
        return header.succeeded

    def play_queue(self, player_id, queue_id):
        header, payload = self._pytheos.api.call('player', 'play_queue', pid=player_id, qid=queue_id)
        return header.succeeded
