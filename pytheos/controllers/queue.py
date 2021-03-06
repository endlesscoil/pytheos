#!/usr/bin/env python
from __future__ import annotations

import asyncio

from .containers import MediaItem
from .. import models

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pytheos import Pytheos


class Queue:
    """ High-level Queue Representation """

    def __init__(self, pytheos: 'Pytheos', player: 'models.Player'):
        self._pytheos = pytheos
        self._player = player
        self._queue = []

    def __len__(self):
        return len(self._queue)

    def __str__(self):
        return '[{items}]'.format(items=', '.join([f'"{str(qi)}"' for qi in self._queue]))

    def __iter__(self):
        return iter(self._queue)

    async def append(self, obj: models.Source):
        """ Inserts a MediaItem at the end of the queue.

        :param obj: MediaItem
        :return: None
        """
        await self.insert(-1, obj)

    async def prepend(self, obj: models.Source):
        """ Inserts a MediaItem at the beginning of the queue.

        :param obj: MediaItem
        :return: None
        """
        await self.insert(0, obj)

    async def insert(self, index: int, obj: models.Source):
        """ Inserts a MediaItem into the specified location in the queue.

        :param index: Index
        :param obj: MediaItem
        :return: None
        """
        if index < 0:
            index = len(self._queue) + index + 1

        await self._refresh_queue(force=True)
        await self._insert_queue_item(index, obj)

    async def replace(self, index: int, obj: models.Source):
        """ Replaces an existing index with a new track.

        :param index: Index
        :param obj: Source item
        :return: None
        """
        await self._refresh_queue(force=True)
        if index >= len(self._queue):
            raise ValueError("Index out of range")

        if index < 0:
            index = len(self._queue) + index + 1

        await self.delete(index)
        await self._refresh_queue(force=True)
        await self._insert_queue_item(index, obj)

    async def delete(self, index):
        await self._refresh_queue(force=True)

        if self._queue:
            if index < 0:
                index = len(self._queue) + index

            await self._pytheos.api.player.remove_from_queue(self._player.player_id, (index + 1,))
            del self._queue[index]

    async def play(self, play_id: int=None):
        """ Starts playing the queue.  Optionally takes a queue ID to play.

        :param play_id: Queue ID
        :return: None
        """
        await self._refresh_queue()

        if self._queue:
            if play_id is None:
                play_id = self._queue[0].queue_id

            await self._pytheos.api.player.play_queue(self._player.player_id, play_id)

    async def next(self):
        """ Plays the next track in the queue.

        :return: None
        """
        await self._pytheos.api.player.play_next(self._player.player_id)

    async def previous(self):
        """ Plays the previous track in the queue.

        :return: None
        """
        await self._pytheos.api.player.play_previous(self._player.player_id)

    async def stop(self):
        """ Stops the current player.

        :return:
        """
        await self._pytheos.api.player.set_play_state(self._player.player_id, models.player.PlayState.Stopped)

    async def resume(self):
        """ Resumes the current player.

        :return: None
        """
        await self._pytheos.api.player.set_play_state(self._player.player_id, models.player.PlayState.Playing)

    async def save(self, name: str):
        """ Saves the queue to the playlists with the specified name.

        :param name: Playlist name
        :return: None
        """
        await self._pytheos.api.player.save_queue(self._player.player_id, name)

    async def clear(self):
        """ Clears the queue.

        :return: None
        """
        await self._refresh_queue(True)
        if self._queue:
            await self._pytheos.api.player.clear_queue(self._player.player_id)

        await self._refresh_queue(True)

    async def refresh(self):
        """ Refreshes the queue.

        :return: None
        """
        await self._refresh_queue(force=True)

    async def _insert_queue_item(self, index: int, obj: models.Source):
        """ Provides the logic to properly do an insertion using the HEOS API.  This removes the items after the insertion
        point, adds the new track to the queue, and then re-adds the removed items to finish the queue.

        :param index: Index to insert at
        :param obj: MediaItem to insert
        :return: None
        """
        to_move = []
        if index < len(self._queue):
            for qi in self._queue[index:]:
                to_move.append(qi.queue_id)

        kwargs = {}
        if obj.media_id:
            kwargs['media_id'] = obj.media_id
        await self._pytheos.api.browse.add_to_queue(self._player.player_id, obj.source_id, obj.container_id, add_type=models.browse.AddToQueueType.AddToEnd, **kwargs)

        await asyncio.sleep(0.5)     # FIXME - Need to wait to give HEOS a time to catch up.  Find a better way to deal with this... ugh.

        if to_move:
            await self._pytheos.api.player.move_queue_item(self._player.player_id, to_move, len(self._queue) + 1)

        await self._refresh_queue(True)

    async def _refresh_queue(self, force: bool=False):
        """ Refreshes the queue if it is uninitialized, this call is forced, or if caching is disabled.

        :param force: Force refresh
        :return: None
        """
        if self._queue is None or force:
            self._queue = [MediaItem(self._pytheos, qi, None) for qi in await self._pytheos.api.player.get_queue(self._player.player_id)]

        return self._queue
