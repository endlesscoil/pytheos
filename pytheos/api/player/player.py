#!/usr/bin/env python
""" Provides the API abstraction for the 'player' command group """

from __future__ import annotations

from typing import Optional

from ..api import API
from .types import Player, QueueItem
from ...errors import InvalidResponse


class PlayerAPI(API):
    """ API interface for the 'player' command group """

    def check_update(self, player_id: int) -> bool:
        """ Checks whether or not there is an update available for the player

        :param player_id: Player ID
        :return: bool
        """
        results = self._pytheos.api.call('player', 'check_update', pid=player_id)
        return results.payload.get('update') == 'update_exist'

    def clear_queue(self, player_id: int) -> None:
        """ Clears the current play queue

        :param player_id: Player ID
        :return: None
        """
        self._pytheos.api.call('player', 'clear_queue', pid=player_id)

    def get_mute(self, player_id: int) -> bool:
        """ Returns whether or not the player is currently muted

        :param player_id: Player ID
        :return: bool
        """
        results = self._pytheos.api.call('player', 'get_mute', pid=player_id)
        return results.header.vars.get('state') == 'on'

    def get_players(self) -> list:
        """ Retrieves a list of players that are available

        :return: list
        """
        results = self._pytheos.api.call('player', 'get_players')
        return [Player(player_data) for player_data in results.payload]

    def get_player_info(self, player_id: int) -> Player:
        """ Retrieves the Player information for a given ID

        :param player_id: Player ID
        :return: Player
        """
        results = self._pytheos.api.call('player', 'get_player_info', pid=player_id)
        return Player(results.payload)

    def get_play_state(self, player_id: int) -> Optional[str]:
        """ Retrieves the current playing state (e.g. play, pause, stop)

        :param player_id: Player ID
        :raises: InvalidResponse
        :return: str
        """
        results = self._pytheos.api.call('player', 'get_play_state', pid=player_id)
        if 'state' not in results.header.vars:
            raise InvalidResponse('Could not find "state" entry in response', results)

        return results.header.vars['state']

    def get_queue(self, player_id: int, range_start: int=0, number_to_retrieve: int=100) -> list:
        """ Retrieves the current play queue

        :param player_id: Player ID
        :param range_start: Optional range to start retrieving from
        :param number_to_retrieve: Number of items to retrieve
        :raises: AssertionError
        :return: list
        """
        assert range_start >= 0
        assert 0 < number_to_retrieve <= 100

        results = self._pytheos.api.call('player', 'get_queue',
                                         pid=player_id, range=f'{range_start},{range_start + number_to_retrieve - 1}')
        return [QueueItem(item) for item in results.payload]

    def get_volume(self, player_id: int) -> int:
        """ Retrieves the current volume

        :param player_id: Player ID
        :return: int
        """
        results = self._pytheos.api.call('player', 'get_volume', pid=player_id)
        return int(results.header.vars.get('level'))

    def play_next(self, player_id: int)-> None:
        """ Plays the next item in the play queue

        :param player_id: Player ID
        :return: None
        """
        self._pytheos.api.call('player', 'play_next', pid=player_id)

    def play_previous(self, player_id: int) -> None:
        """ Plays the previous item in the play queue

        :param player_id: Player ID
        :return: None
        """
        self._pytheos.api.call('player', 'play_previous', pid=player_id)

    def play_queue(self, player_id: int, queue_entry_id: int) -> None:
        """ Plays the specified queue item

        :param player_id: Player ID
        :param queue_entry_id: Queue entry ID
        :return: None
        """
        self._pytheos.api.call('player', 'play_queue', pid=player_id, qid=queue_entry_id)
