#!/usr/bin/env python
""" Provides the API abstraction for the 'player' command group """

from __future__ import annotations

from typing import Optional, Union, List

from .. import models
from ..networking.errors import InvalidResponse


class PlayerAPI:
    """ API interface for the 'player' command group """

    VOLUME_MIN = 0
    VOLUME_MAX = 100
    VOLUME_DEFAULT_STEP = 5

    def __init__(self, conn):
        self._api = conn

    async def check_update(self, player_id: int) -> bool:
        """ Checks whether or not there is an update available for the player

        :param player_id: Player ID
        :return: bool
        """
        results = await self._api.call('player', 'check_update', pid=player_id)
        return results.payload.get('update') == 'update_exist'

    async def clear_queue(self, player_id: int) -> None:
        """ Clears the current play queue

        :param player_id: Player ID
        :return: None
        """
        await self._api.call('player', 'clear_queue', pid=player_id)

    async def get_mute(self, player_id: int) -> bool:
        """ Returns whether or not the player is currently muted

        :param player_id: Player ID
        :return: bool
        """
        results = await self._api.call('player', 'get_mute', pid=player_id)
        return results.header.vars.get('state') == 'on'

    async def get_now_playing_media(self, player_id: int) -> models.media.MediaItem:
        """ Returns details of the currently playing media

        :param player_id: PlayerID
        :return: MediaItem
        """
        results = await self._api.call('player', 'get_now_playing_media', pid=player_id)
        # TODO: options support

        return models.media.MediaItem(results.payload)

    async def get_players(self) -> List[models.Player]:
        """ Retrieves a list of players that are available

        :return: list
        """
        results = await self._api.call('player', 'get_players')
        return [models.Player(player_data) for player_data in results.payload]

    async def get_player_info(self, player_id: int) -> models.Player:
        """ Retrieves the Player information for a given ID

        :param player_id: Player ID
        :return: Player
        """
        results = await self._api.call('player', 'get_player_info', pid=player_id)
        return models.Player(results.payload)

    async def get_play_mode(self, player_id: int) -> models.player.PlayMode:
        """ Returns the current play mode flags - repeat & shuffle

        :param player_id: Player ID
        :return: PlayMode
        """
        results = await self._api.call('player', 'get_play_mode', pid=player_id)

        return models.player.PlayMode(
            repeat=models.player.RepeatMode(results.header.vars.get('repeat')),
            shuffle=models.player.ShuffleMode(results.header.vars.get('shuffle'))
        )

    async def get_play_state(self, player_id: int) -> models.player.PlayState:
        """ Retrieves the current playing state (e.g. play, pause, stop)

        :param player_id: Player ID
        :raises: InvalidResponse
        :return: str
        """
        results = await self._api.call('player', 'get_play_state', pid=player_id)
        if 'state' not in results.header.vars:
            raise InvalidResponse('Could not find "state" entry in response', results)

        return models.player.PlayState(results.header.vars['state'])

    async def get_queue(self, player_id: int, range_start: int=0, number_to_retrieve: int=100) -> list:
        """ Retrieves the current play queue

        :param player_id: Player ID
        :param range_start: Optional range to start retrieving from
        :param number_to_retrieve: Number of items to retrieve
        :raises: ValueError
        :return: list
        """
        if range_start < 0:
            raise ValueError('Range start must be >= 0')
        if not 0 < number_to_retrieve <= 100:
            raise ValueError('Number of items to retrieve must be between 1 and 100')

        results = await self._api.call('player', 'get_queue',
                                       pid=player_id, range=f'{range_start},{range_start + number_to_retrieve - 1}')
        return [models.media.MediaItem(item) for item in results.payload]

    async def get_quickselects(self, player_id: int, quick_select_id: Optional[int]=None) -> list:
        """ Retrieves a list of quick select entries - LEGO AVR or HEOS BAR only

        :param player_id: Player ID
        :param quick_select_id: QuickSelect ID
        :raises: ValueError
        :return: list
        """
        if quick_select_id is not None and not 0 < quick_select_id <= 6:
            raise ValueError('Quick Select ID must be between 1 and 6 or None to retrieve all Quick Selects')

        kwargs = {'pid': player_id}
        if quick_select_id is not None:
            kwargs['id'] = quick_select_id

        results = await self._api.call('player', 'get_quickselects', **kwargs)
        return [models.player.QuickSelect(id=item['id'], name=item['name']) for item in results.payload]

    async def get_volume(self, player_id: int) -> int:
        """ Retrieves the current volume

        :param player_id: Player ID
        :return: int
        """
        results = await self._api.call('player', 'get_volume', pid=player_id)
        return int(results.header.vars.get('level'))

    async def move_queue_item(self, player_id: int, queue_ids: tuple, destination_queue_id: int):
        """ Moves the specified queue IDs to the location specified by the destination queue ID.

        :param player_id: Player ID
        :param queue_ids: Tuple of Queue IDs
        :param destination_queue_id: Destination Queue ID
        :raises ValueError:
        :return: None
        """
        quickselect_ids = []
        for qid in queue_ids:
            if qid < 1:
                raise ValueError('Invalid Queue ID - must be between 1 and the size of the queue')

            quickselect_ids.append(str(qid))

        if destination_queue_id < 1:
            raise ValueError('Invalid Queue ID - must be between 1 and the size of the queue')

        await self._api.call('player', 'move_queue_item', pid=player_id, sqid=','.join(quickselect_ids), dqid=destination_queue_id)

    async def play_next(self, player_id: int) -> None:
        """ Plays the next item in the play queue

        :param player_id: Player ID
        :return: None
        """
        await self._api.call('player', 'play_next', pid=player_id)

    async def play_previous(self, player_id: int) -> None:
        """ Plays the previous item in the play queue

        :param player_id: Player ID
        :return: None
        """
        await self._api.call('player', 'play_previous', pid=player_id)

    async def play_queue(self, player_id: int, queue_entry_id: int) -> None:
        """ Plays the specified queue item

        :param player_id: Player ID
        :param queue_entry_id: Queue entry ID
        :return: None
        """
        await self._api.call('player', 'play_queue', pid=player_id, qid=queue_entry_id)

    async def play_quickselect(self, player_id: int, quick_select_id: int) -> None:
        """ Play the specified QuickSelect ID

        :param player_id: Player ID
        :param quick_select_id: QuickSelect ID
        :raises: ValueError
        :return: None
        """
        if not 1 <= quick_select_id <= 6:
            raise ValueError('Quick Select ID must be between 1 and 6')

        await self._api.call('player', 'play_quickselect', pid=player_id, id=quick_select_id)

    async def remove_from_queue(self, player_id: int, queue_ids: Union[list, tuple, set]) -> None:
        """ Remove a set of items from the queue

        :param player_id: Player ID
        :param queue_ids: Queue IDs
        :return: None
        """
        await self._api.call('player', 'remove_from_queue', pid=player_id, qid=','.join([str(qid) for qid in queue_ids]))

    async def save_queue(self, player_id: int, playlist_name: str) -> None:
        """ Saves the current queue as a playlist

        :param player_id: Player ID
        :param playlist_name: Playlist name
        :raises: ValueError
        :return: None
        """
        if len(playlist_name) > 128:
            raise ValueError('Playlist name cannot exceed 128 characters')

        await self._api.call('player', 'save_queue', pid=player_id, name=playlist_name)

    async def set_mute(self, player_id: int, enable: bool) -> None:
        """ Enables or disables mute on the specified player

        :param player_id: Player ID
        :param enable: True or False
        :return: None
        """
        await self._api.call('player', 'set_mute', pid=player_id, state=models.player.Mute.On if enable else models.player.Mute.Off)

    async def set_play_mode(self, player_id: int, play_mode: models.player.PlayMode) -> None:
        """ Sets the play mode for the specified player - repeat & shuffle

        :param player_id: Player ID
        :param play_mode: PlayMode
        :return: None
        """
        await self._api.call('player', 'set_play_mode', pid=player_id, repeat=play_mode.repeat, shuffle=play_mode.shuffle)

    async def set_quickselect(self, player_id: int, quickselect_id: int) -> None:
        """ Selects the specified Quick Select

        :param player_id: Player ID
        :param quickselect_id: QuickSelect ID
        :raises: ValueError
        :return: None
        """
        if not 0 < quickselect_id <= 6:
            raise ValueError('Level must be between 1 and 6')

        await self._api.call('player', 'set_quickselect', pid=player_id, id=quickselect_id)

    async def set_play_state(self, player_id: int, state: models.player.PlayState) -> None:
        """ Set the current playing state for the player

        :param player_id: Player ID
        :param state: Play state
        :raises: ValueError
        :return: None
        """
        await self._api.call('player', 'set_play_state', pid=player_id, state=models.player.PlayState(state))

    async def set_volume(self, player_id: int, level: int) -> None:
        """ Sets the volume level on the player

        :param player_id: Player ID
        :param level: Volume level
        :raises: ValueError
        :return: None
        """
        if not self.VOLUME_MIN <= level <= self.VOLUME_MAX:
            raise ValueError('Level must be between 0 and 100')

        await self._api.call('player', 'set_volume', pid=player_id, level=level)

    async def toggle_mute(self, player_id: int) -> None:
        """ Toggles mute on the player

        :param player_id: Player ID
        :return: None
        """
        await self._api.call('player', 'toggle_mute', pid=player_id)

    async def volume_up(self, player_id: int, step_level: int=VOLUME_DEFAULT_STEP) -> None:
        """ Turn the volume up by the specified step level.

        :param player_id: Player ID
        :param step_level: Step level
        :raises: ValueError
        :return: None
        """
        if not 0 < step_level <= 10:
            raise ValueError('Step level must be between 1 and 10')

        await self._api.call('player', 'volume_up', pid=player_id, step=step_level)

    async def volume_down(self, player_id: int, step_level: int=VOLUME_DEFAULT_STEP) -> None:
        """ Turn the volume down by the specified step level.

        :param player_id: Player ID
        :param step_level: Step level
        :raises: ValueError
        :return: None
        """
        if not 0 < step_level <= 10:
            raise ValueError('Step level must be between 1 and 10')

        await self._api.call('player', 'volume_down', pid=player_id, step=step_level)
