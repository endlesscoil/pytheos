#!/usr/bin/env python
from collections.abc import MutableSequence
from typing import TYPE_CHECKING

from pytheos.models.browse import AddToQueueType
from pytheos.models.player import PlayState
from pytheos.source import PytheosMedia

if TYPE_CHECKING:
    from pytheos import Pytheos
    from pytheos.api.player import Player


class PytheosQueue(MutableSequence):
    """ High-level Queue Representation """

    @staticmethod
    def _get_queue_insert_ids(item):
        cid = item.id if item.is_container_type else item.parent.id
        mid = None if item.is_container_type else item.id

        return cid, mid

    def __init__(self, pytheos: 'Pytheos', player: 'Player'):
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
        self._pytheos.api.player.remove_from_queue(self._player.player_id, (key + 1,))
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

    def insert(self, index: int, obj: PytheosMedia):
        """ Inserts a MediaItem into the specified location in the queue.

        :param index: Index
        :param obj: MediaItem
        :return: None
        """
        self._refresh_queue()
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
        self._pytheos.api.player.set_play_state(self._player.player_id, PlayState.Stopped)

    def resume(self):
        """ Resumes the current player.

        :return: None
        """
        self._pytheos.api.player.set_play_state(self._player.player_id, PlayState.Playing)

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

    def _insert_queue_item(self, index: int, obj: PytheosMedia):
        """ Provides the logic to properly do an insertion using the HEOS API.  This removes the items after the insertion
        point, adds the new track to the queue, and then re-adds the removed items to finish the queue.

        :param index: Index to insert at
        :param obj: MediaItem to insert
        :return: None
        """
        if self._queue and index + 1 < len(self._queue):
            self._pytheos.api.player.remove_from_queue(self._player.player_id, list(range(index + 1, len(self._queue))))

        cid, mid = PytheosQueue._get_queue_insert_ids(obj)
        self._pytheos.api.browse.add_to_queue(self._player.player_id, obj.parent.source_id, cid, media_id=mid, add_type=AddToQueueType.AddToEnd)

        for qi in self._queue[index:]:
            cid, mid = PytheosQueue._get_queue_insert_ids(qi)
            self._pytheos.api.browse.add_to_queue(self._player.player_id, qi.parent.source_id, cid, media_id=mid, add_type=AddToQueueType.AddToEnd)

        self._refresh_queue(True)

    def _refresh_queue(self, force: bool=False):
        """ Refreshes the queue if it is uninitialized, this call is forced, or if caching is disabled.

        :param force: Force refresh
        :return: None
        """
        if self._queue is None or self.nocache or force:
            self._queue = [PytheosMedia(self._pytheos, qi, None) for qi in self._pytheos.api.player.get_queue(self._player.player_id)]

        return self._queue
