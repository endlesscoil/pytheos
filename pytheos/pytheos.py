#!/usr/bin/env python
""" Provides the primary interface into the library """

from __future__ import annotations

import logging
import queue
from typing import Callable, Optional, Union

from . import utils
from .api.interface import APIInterface
from .connection import Connection
from .errors import ChannelUnavailableError
from .events.handler import EventHandlerThread
from .events.receiver import EventReceiverThread
from .group import PytheosGroup
from .player import PytheosPlayer
from .source import PytheosSource
from .types import HEOSEvent, SSDPResponse, AccountStatus

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('pytheos')


def connect(host: Union[Pytheos, tuple, str]) -> Pytheos:
    """ Connect to the provided host and return a context manager for use with the connection.

    :param host: Host to connect to
    :raises: ValueError
    :return: The Pytheos instance
    """
    conn = None
    port = None

    if isinstance(host, Pytheos):
        conn = host
    elif isinstance(host, tuple):
        host, port = host
    elif isinstance(host, str) and ':' in host:
        host, port = host.split(':')
        port = int(port)
    else:
        raise ValueError(f'Unrecognized host format: {host}')

    if not conn:
        conn = Pytheos(host, port)

    return conn.connect()


class Pytheos:
    """ Pytheos interface """
    DEFAULT_PORT = 1255

    @property
    def log_level(self):
        return logger.level

    @log_level.setter
    def log_level(self, value):
        logger.setLevel(value)

    @property
    def connected(self):
        return self._connected

    @property
    def signed_in(self):
        return self._account_status == AccountStatus.SignedIn

    @property
    def username(self):
        return self._account_username

    @property
    def players(self) -> tuple:
        if self._players is None:
            self.get_players()

        return tuple(self._players)

    @property
    def groups(self) -> tuple:
        if self._groups is None:
            self.get_groups()

        return tuple(self._groups)

    @property
    def sources(self) -> tuple:
        if self._sources is None:
            self.get_sources()

        return tuple(self._sources)

    @property
    def receive_events(self):
        return self._receive_events

    @receive_events.setter
    def receive_events(self, value):
        self._receive_events = value
        self._set_register_for_change_events(value)

    def __init__(self, server: Optional[str]=None, port: Optional[int]=DEFAULT_PORT, from_response: SSDPResponse=None):
        """ Constructor

        :param server: Server hostname or IP
        :param port: Port number
        :param from_response: Optional SSDP response to extract location data from
        """
        if from_response:
            server = utils.extract_host(from_response.location)

        self.server: str = server
        self.port: int = port

        self._command_channel = Connection()
        self._event_channel = Connection()
        self._event_thread: Optional[EventReceiverThread] = None
        self._event_handler_thread: Optional[EventHandlerThread] = None
        self._connected = False
        self._event_subscriptions = {}
        self._receive_events = True

        self._account_status: Optional[AccountStatus] = None
        self._account_username: Optional[str] = None
        self._players: Optional[dict] = None
        self._groups: Optional[dict] = None
        self._sources: Optional[dict] = None

        self.api: APIInterface = APIInterface(self._command_channel)

        self._init_internal_event_handlers()

    def __repr__(self):
        return f'<Pytheos(server={self.server}, port={self.port})>'

    def __enter__(self):
        if not self._connected:
            self.connect()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connected:
            self.close()

    def connect(self, enable_event_connection: bool=True, refresh: bool=True) -> Pytheos:
        """ Connect to our HEOS device.

        :param enable_event_connection: Enables establishing an additional connection for system events
        :param refresh: Determines if the system state should be automatically refreshed
        :return: self
        """
        logger.info(f'Connecting to {self.server}:{self.port}')

        self._command_channel.connect(self.server, self.port)
        self._connected = True

        self._receive_events = enable_event_connection
        if self._receive_events:
            self._event_channel.connect(self.server, self.port, deduplicate=True)
            self._set_register_for_change_events(True)

            # FIXME: Figure out exactly how I'm consuming these.
            self._event_queue = queue.Queue()
            self._event_thread = EventReceiverThread(self._event_channel, self._event_queue)
            self._event_thread.start()
            self._event_handler_thread = EventHandlerThread(self, self._event_queue)
            self._event_handler_thread.start()
            #/FIXME

        if refresh:
            self.refresh()

        return self

    def _set_register_for_change_events(self, value: bool):
        APIInterface(self._event_channel).system.register_for_change_events(value)

    def close(self):
        """ Close the connection to our HEOS device

        :return: None
        """
        logger.info(f'Closing connection to {self.server}:{self.port}')
        if self._event_thread:
            self._event_thread.stop()
            self._event_thread.join()

        if self._event_handler_thread:
            self._event_handler_thread.stop()
            self._event_handler_thread.join()

        if self._event_channel:
            self._event_channel.close()

        if self._command_channel:
            self._command_channel.close()

        self._connected = False

    def subscribe(self, event_name: str, callback: Callable):
        """ Subscribe a callback function to a specific event

        :param event_name: Event name
        :param callback: Callback function
        :return: None
        """
        # FIXME: Change event_name to an enum
        if self._event_subscriptions.get(event_name) is None:
            self._event_subscriptions[event_name] = []

        self._event_subscriptions[event_name].append(callback)

    def refresh(self):
        """ Refreshes internal information from the HEOS system.

        :return: None
        """
        self.check_account()
        self.get_players()
        self.get_groups()
        self.get_sources()

    def reboot(self):
        """ Instructs the system to reboot.

        :return: None
        """
        self.api.system.reboot()

    def check_account(self) -> tuple:
        """ Checks if the system is logged into HEOS and returns the status and account name, if available.

        :return: tuple
        """
        self._account_status, self._account_username = self.api.system.check_account()

        return self._account_status, self._account_username

    def sign_in(self, username: str, password: str):
        """ Signs the system into the HEOS service.

        :param username: Username
        :param password: Password
        :return: None
        """
        self.api.system.sign_in(username, password)

    def sign_out(self):
        """ Signs out from the HEOS service.

        :return: None
        """
        self.api.system.sign_out()

    def get_players(self):
        """ Retrieves a mapping of IDs to Players present in the HEOS system.

        :return: dict
        """
        self._players = {}

        for player in self.api.player.get_players():
            self._players[player.player_id] = PytheosPlayer(self, player)

        return self._players

    def get_groups(self):
        """ Retrieves a mapping of IDs to Groups present in the HEOS system.

        :return: dict
        """
        self._groups = {}

        for group in self.api.group.get_groups():
            self._groups[group.group_id] = PytheosGroup(self, group)

        return self._groups

    def get_sources(self):
        """ Retrieves a mapping of IDs to Sources present in the HEOS system.

        :return:
        """
        self._sources = {}

        for source in self.api.browse.get_music_sources():
            self._sources[source.source_id] = PytheosSource(self, source)

        return self._sources

    def _check_channel_availability(self, channel: Connection):
        """ Checks to make sure that the provided channel is available.

        :param channel: Channel connection
        :raises: ChannelUnavailableError
        :return: None
        """
        if not channel or not channel.connected:
            raise ChannelUnavailableError()

    def _event_handler(self, event: HEOSEvent):
        """ Internal event handler

        :param event: HEOS Event
        :return: None
        """
        for callback in self._event_subscriptions.get(event.command, []):
            callback(event)

    def _init_internal_event_handlers(self):
        """ Initialize the internal event handlers

        :return: None
        """
        # FIXME: Meh, do something better with this.
        internal_handler_map = {
            # 'event/sources_changed': self._handle_sources_changed,
            # 'event/players_changed': self._handle_players_changed,
            # 'event/groups_changed': self._handle_groups_changed,
            # 'event/player_state_changed': self._handle_player_state_changed,
            # 'event/player_now_playing_changed': self._handle_now_playing_changed,
            # 'event/player_now_playing_progress': self._handle_now_playing_progress,
            # 'event/player_playback_error': self._handle_playback_error,
            # 'event/player_queue_changed': self._handle_queue_changed,
            # 'event/player_volume_changed': self._handle_volume_changed,
            # 'event/repeat_mode_changed': self._handle_repeat_mode_changed,
            # 'event/shuffle_mode_changed': self._handle_shuffle_mode_changed,
            # 'event/group_volume_changed': self._handle_group_volume_changed,
            # 'event/user_changed': self._handle_user_changed,
        }

        for event, callback in internal_handler_map.items():
            self.subscribe(event, callback)

    def _handle_sources_changed(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_players_changed(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_groups_changed(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_player_state_changed(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_now_playing_changed(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_now_playing_progress(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_playback_error(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_queue_changed(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_volume_changed(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_repeat_mode_changed(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_shuffle_mode_changed(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_group_volume_changed(self, event: HEOSEvent):
        raise NotImplementedError()

    def _handle_user_changed(self, event: HEOSEvent):
        raise NotImplementedError()
