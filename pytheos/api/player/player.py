#!/usr/bin/env python
from __future__ import annotations

from ..api import API
from .types import Player, QueueItem


class PlayerAPI(API):
    def check_update(self, player_id):
        results = self._pytheos.api.call('player', 'check_update', pid=player_id)

        update = None
        if results.payload:
            update = results.payload.get('update')

        return update == 'update_exist'

    def clear_queue(self, player_id):
        self._pytheos.api.call('player', 'clear_queue', pid=player_id)

    def get_mute(self, player_id):
        results = self._pytheos.api.call('player', 'get_mute', pid=player_id)
        return results.message_vars.get('state') == 'on'

    def get_players(self):
        results = self._pytheos.api.call('player', 'get_players')

        players = []
        for player_data in results.payload:
            players.append(Player(player_data))

        return players

    def get_player_info(self, player_id):
        results = self._pytheos.api.call('player', 'get_player_info', pid=player_id)
        return Player(results.payload)

    def get_play_state(self, player_id):
        results = self._pytheos.api.call('player', 'get_play_state', pid=player_id)
        return results.message_vars.get('state')

    def get_queue(self, player_id, range_start, range_end):
        results = self._pytheos.api.call('player', 'get_queue', pid=player_id, range=f'{range_start},{range_end}')

        queue = []
        for entry in results.payload:
            queue.append(QueueItem(from_dict=entry))

        return queue

    def get_volume(self, player_id):
        results = self._pytheos.api.call('player', 'get_volume', pid=player_id)
        volume = results.message_vars.get('level')
        return int(volume) if volume is not None else None # FIXME: Do we really need to be returning None here?

    def play_next(self, player_id):
        self._pytheos.api.call('player', 'play_next', pid=player_id)

    def play_previous(self, player_id):
        self._pytheos.api.call('player', 'play_previous', pid=player_id)

    def play_queue(self, player_id, queue_id):
        self._pytheos.api.call('player', 'play_queue', pid=player_id, qid=queue_id)
