#!/usr/bin/env python
from __future__ import annotations

import time
from collections.abc import MutableSequence

from .containers import MediaItem
from .. import models

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pytheos import Pytheos


class Queue(MutableSequence):
    """ High-level Queue Representation """

    def __init__(self, pytheos: 'Pytheos', player: 'models.Player'):
        super().__init__()

        self._pytheos = pytheos
        self._player = player
        self._queue = None
        self._nocache = False

    def __getitem__(self, item):
        self._refresh_queue()
        return self._queue[item]

    def __setitem__(self, key, value):
        self._refresh_queue()
        self._insert_queue_item(key, value)

    def __delitem__(self, key):
        self._refresh_queue()

        if self._queue:
            # Replace a negative index with a positive one
            if key < 0:
                key = len(self._queue) + key

            self._pytheos.api.player.remove_from_queue(self._player.player_id, (key + 1,))
            del self._queue[key]

    def __len__(self):
        self._refresh_queue()
        return len(self._queue)

    def __str__(self):
        self._refresh_queue()
        return '[{items}]'.format(items=', '.join([str(qi) for qi in self._queue]))

    @property
    def nocache(self):
        return self._nocache

    @nocache.setter
    def nocache(self, value):
        self._nocache = value

    def insert(self, index: int, obj: models.Source):
        """ Inserts a MediaItem into the specified location in the queue.

        :param index: Index
        :param obj: MediaItem
        :return: None
        """
        self._refresh_queue(force=True)
        self._insert_queue_item(index, obj)

    def replace(self, index: int, obj: models.Source):
        """ Replaces an existing index with a new track.

        :param index: Index
        :param obj: Source item
        :return: None
        """
        self._refresh_queue(force=True)
        if index >= len(self._queue):
            raise ValueError("Index out of range")

        del self[index]
        self._refresh_queue(force=True)
        self._insert_queue_item(index, obj)

    def play(self, play_id: int=None):
        """ Starts playing the queue.  Optionally takes a queue ID to play.

        :param play_id: Queue ID
        :return: None
        """
        self._refresh_queue()

        if self._queue:
            if play_id is None:
                play_id = self._queue[0].queue_id

            self._pytheos.api.player.play_queue(self._player.player_id, play_id)

    def next(self):
        """ Plays the next track in the queue.

        :return: None
        """
        self._pytheos.api.player.play_next(self._player.player_id)

    def previous(self):
        """ Plays the previous track in the queue.

        :return: None
        """
        self._pytheos.api.player.play_previous(self._player.player_id)

    def stop(self):
        """ Stops the current player.

        :return:
        """
        self._pytheos.api.player.set_play_state(self._player.player_id, models.player.PlayState.Stopped)

    def resume(self):
        """ Resumes the current player.

        :return: None
        """
        self._pytheos.api.player.set_play_state(self._player.player_id, models.player.PlayState.Playing)

    def save(self, name: str):
        """ Saves the queue to the playlists with the specified name.

        :param name: Playlist name
        :return: None
        """
        self._pytheos.api.player.save_queue(self._player.player_id, name)

    def clear(self):
        """ Clears the queue.

        :return: None
        """
        self._refresh_queue(True)
        if self._queue:
            self._pytheos.api.player.clear_queue(self._player.player_id)

        self._refresh_queue(True)

    def refresh(self):
        """ Refreshes the queue.

        :return: None
        """
        self._refresh_queue(force=True)

    def _insert_queue_item(self, index: int, obj: models.Source):
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
        self._pytheos.api.browse.add_to_queue(self._player.player_id, obj.source_id, obj.container_id, add_type=models.browse.AddToQueueType.AddToEnd, **kwargs)

        time.sleep(0.5)     # FIXME - Need to wait to give HEOS a time to catch up.  Find a better way to deal with this... ugh.

        if to_move:
            self._pytheos.api.player.move_queue_item(self._player.player_id, to_move, len(self._queue) + 1)

        self._refresh_queue(True)

    def _refresh_queue(self, force: bool=False):
        """ Refreshes the queue if it is uninitialized, this call is forced, or if caching is disabled.

        :param force: Force refresh
        :return: None
        """
        if self._queue is None or self.nocache or force:
            self._queue = [MediaItem(self._pytheos, qi, None) for qi in self._pytheos.api.player.get_queue(self._player.player_id)]

        return self._queue
