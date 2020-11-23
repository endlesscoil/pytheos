#!/usr/bin/env python
""" High level abstraction of a HEOS Player """

from __future__ import annotations

from .. import models, controllers

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from pytheos import Pytheos


class Player:
    """ High-level Player API """

    @property
    def id(self) -> str:
        return self._player.player_id

    @property
    def name(self) -> str:
        return self._player.name

    @property
    def group(self) -> controllers.Group:
        return self._pytheos.get_group(self._player.group_id)

    @property
    def model(self) -> str:
        return self._player.model

    @property
    def version(self) -> str:
        return self._player.version

    @property
    def network(self) -> models.player.Network:
        return self._player.network

    @property
    def ip(self) -> str:
        return self._player.ip

    @property
    def line_out(self) -> models.player.Lineout:
        return self._player.lineout

    @property
    def control(self) -> models.player.Control:
        return self._player.control

    @property
    def serial(self) -> str:
        return self._player.serial

    @property
    def update_available(self) -> bool:
        return self._pytheos.api.player.check_update(self.id)

    @property
    def mute(self) -> bool:
        return self._pytheos.api.player.get_mute(self.id)

    @mute.setter
    def mute(self, value: bool):
        self._pytheos.api.player.set_mute(self.id, value)

    @property
    def repeat(self) -> models.player.RepeatMode:
        repeat, shuffle = self._get_play_mode()

        return repeat

    @repeat.setter
    def repeat(self, value: models.player.RepeatMode):
        self._pytheos.api.player.set_play_mode(self.id, models.player.PlayMode(repeat=value, shuffle=self.shuffle))
        self._repeat = value

    @property
    def shuffle(self) -> models.player.ShuffleMode:
        repeat, shuffle = self._get_play_mode()

        return shuffle

    @shuffle.setter
    def shuffle(self, value: models.player.ShuffleMode):
        self._pytheos.api.player.set_play_mode(self.id, models.player.PlayMode(repeat=self.repeat, shuffle=value))
        self._shuffle = value

    @property
    def playing(self) -> bool:
        return self.play_state == models.player.PlayState.Playing

    @playing.setter
    def playing(self, value: bool):
        self._pytheos.api.player.set_play_state(self.id, models.player.PlayState.Playing if value else models.player.PlayState.Stopped)

    @property
    def paused(self) -> bool:
        return self.play_state == models.player.PlayState.Paused

    @paused.setter
    def paused(self, value: bool):
        self._pytheos.api.player.set_play_state(self.id, models.player.PlayState.Paused if value else models.player.PlayState.Playing)

    @property
    def stopped(self) -> bool:
        return self.play_state == models.player.PlayState.Stopped

    @stopped.setter
    def stopped(self, value: bool):
        self._pytheos.api.player.set_play_state(self.id, models.player.PlayState.Stopped if value else models.player.PlayState.Playing)

    @property
    def volume(self) -> int:
        return self._pytheos.api.player.get_volume(self.id)

    @volume.setter
    def volume(self, value: int):
        if value < self._pytheos.api.player.VOLUME_MIN:
            value = self._pytheos.api.player.VOLUME_MIN
        elif value > self._pytheos.api.player.VOLUME_MAX:
            value = self._pytheos.api.player.VOLUME_MAX

        self._pytheos.api.player.set_volume(self.id, value)

    @property
    def now_playing(self) -> models.MediaItem:     # FIXME: Maybe want to abstract MediaItem out
        return self._pytheos.api.player.get_now_playing_media(self.id)

    @property
    def play_state(self) -> models.player.PlayState:
        return self._pytheos.api.player.get_play_state(self.id)

    @property
    def quick_selects(self) -> dict:
        return {qs.id: qs for qs in self._pytheos.api.player.get_quickselects(self.id)}

    @property
    def queue(self):
        return self._queue

    def __init__(self, pytheos: 'Pytheos', player: models.Player):
        self._player = player
        self._pytheos = pytheos

        self._mute: Optional[bool] = None
        self._repeat: Optional[models.player.RepeatMode] = None
        self._shuffle: Optional[models.player.ShuffleMode] = None
        self._volume: Optional[int] = None
        self._quick_selects: Optional[dict] = None
        self._play_state: Optional[models.player.PlayState] = None
        self._queue = controllers.Queue(pytheos, player)
        self._now_playing: Optional[models.MediaItem] = None

    def refresh(self, player_id=None):
        """ Retrieve and update the Player information used by this class.  Optionally, the ID already present on the
        instance may be overridden.

        :param player_id: Player ID to use or None to use the currently set ID
        :return: None
        """
        self._player = self._pytheos.api.player.get_player_info(player_id if player_id else self.id)

    def play_input(self, input_source: models.source.InputSource, source_player: Optional[models.Player]=None):
        """ Instructs the player to play the specified input source.  Optionally, this input source can live on another
        Player on the network, which can be specified with the source_player parameter.

        :param input_source: Input source to play
        :param source_player: Optional source Player ID
        :return: None
        """
        source_player_id = source_player.player_id if source_player else None
        self._pytheos.api.browse.play_input(self.id, input_name=input_source, source_player_id=source_player_id)

    def play_favorite(self, favorite: int):
        """ Instructs the player to play the specified favorite or preset ID.

        :param favorite: Favorite/Preset ID
        :return: None
        """
        self._pytheos.api.browse.play_preset(self.id, favorite)

    def play_quickselect(self, quick_select: int):
        """ Instructs the player to play the specified quickselect ID.  This functionality is not available on all
        players.

        :param quick_select: Quickselect ID
        :return: None
        """
        self._pytheos.api.player.play_quickselect(self.id, quick_select)

    def play_url(self, url: str):
        """ Instructs the player to play the specified URL.

        :param url: URL
        :return: None
        """
        self._pytheos.api.browse.play_url(self.id, url)

    def play(self):
        """ Set the current player state to Playing.

        :return: None
        """
        self.playing = True

    resume = play   # Resume and Play are functionally the same.

    def pause(self):
        """ Set the current player state to Paused.

        :return: None
        """
        self.paused = True

    def stop(self):
        """ Set the current player state to Stopped.

        :return: None
        """
        self.stopped = True

    def next(self):
        """ Instructs the player to play the next track.

        :return: None
        """
        self._pytheos.api.player.play_next(self.id)

    def previous(self):
        """ Instructs the player to play the previous track.

        :return: None
        """
        self._pytheos.api.player.play_previous(self.id)

    def _get_play_mode(self) -> tuple:
        """ Retries and returns the Repeat & Shuffle status.

        :return: tuple
        """
        state = self._pytheos.api.player.get_play_mode(self.id)
        return state.repeat, state.shuffle
