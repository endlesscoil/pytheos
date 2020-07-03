#!/usr/bin/env python
""" Provides the primary interface into the library """

from __future__ import annotations

import logging
import queue
from typing import Callable

from . import utils
from .api.interface import APIInterface
from .connection import Connection
from .errors import ChannelUnavailableError
from .events.handler import EventHandlerThread
from .events.receiver import EventReceiverThread
from .types import HEOSEvent, SSDPResponse

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('pytheos')


def connect(host):
    """ Connect to the provided host and return a context manager for use with the connection.

    :param host: Host to connect to
    :raises: ValueError
    :return: Context manager for Pytheos
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

    def __init__(self, server: str=None, port: int=None, from_response: SSDPResponse=None):
        """ Constructor

        :param server: Server hostname or IP
        :param port: Port number
        :param from_response: Optional SSDP response to extract location data from
        """
        if from_response:
            server = utils.extract_host(from_response.location)

        # FIXME: I really don't like these asserts and the default Nones above - find a way to make this better.
        assert server is not None
        assert port is not None
        #/FIXME

        self.server: str = server
        self.port: int = port

        self._command_channel = Connection()
        self._event_channel = Connection()
        self._event_thread = None
        self._event_handler_thread = None
        self._connected = False
        self._event_subscriptions = {}

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

    @property
    def connected(self):
        return self._connected

    @property
    def log_level(self):
        return logger.level

    @log_level.setter
    def log_level(self, value):
        logger.setLevel(value)

    def connect(self, enable_event_connection=True) -> Pytheos:
        """ Connect to our HEOS device.

        :return: self
        """
        logger.info(f'Connecting to {self.server}:{self.port}')

        self._command_channel.connect(self.server, self.port)
        self._connected = True

        if enable_event_connection:
            self._event_channel.connect(self.server, self.port, deduplicate=True)
            APIInterface(self._event_channel).system.register_for_change_events(True)

            # FIXME: Figure out exactly how I'm consuming these.
            self._event_queue = queue.Queue()
            self._event_thread = EventReceiverThread(self._event_channel, self._event_queue)
            self._event_thread.start()
            self._event_handler_thread = EventHandlerThread(self, self._event_queue)
            self._event_handler_thread.start()
            #/FIXME

        # TODO: get status

        return self

    def close(self) -> None:
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

    def subscribe(self, event_name: str, callback: Callable) -> None:
        """ Subscribe a callback function to a specific event

        :param event_name: Event name
        :param callback: Callback function
        :return: None
        """
        # FIXME: Change event_name to an enum
        if self._event_subscriptions.get(event_name) is None:
            self._event_subscriptions[event_name] = []

        self._event_subscriptions[event_name].append(callback)

    def _check_channel_availability(self, channel: Connection) -> None:
        """ Checks to make sure that the provided channel is available.

        :param channel: Channel connection
        :raises: ChannelUnavailableError
        :return: None
        """
        if not channel or not channel.connected:
            raise ChannelUnavailableError()

    def _event_handler(self, event: HEOSEvent) -> None:
        """ Internal event handler

        :param event: HEOS Event
        :return: None
        """
        for callback in self._event_subscriptions.get(event.command, []):
            callback(event)

    def _init_internal_event_handlers(self) -> None:
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
