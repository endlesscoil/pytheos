#!/usr/bin/env python
""" Provides the primary interface into the library """

from __future__ import annotations

import queue
import threading
import time
from typing import Optional, Callable

from . import utils
from .api.container import APIContainer
from .connection import Connection
from .errors import ChannelUnavailableError
from .types import HEOSEvent, HEOSResult, SSDPResponse


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

    class _wrapper(object):
        """ Context wrapper """
        def __enter__(self):
            self.conn = conn
            self.conn.connect()

            return self.conn

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.conn:
                self.conn.close()

    return _wrapper()


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
        self.api: Optional[APIContainer] = None

        self._event_subscriptions = {}
        self._init_internal_event_handlers()

    def __repr__(self):
        return f'<Pytheos(server={self.server}, port={self.port})>'

    def connect(self) -> None:
        """ Connect to our HEOS device

        :return: None
        """
        self._command_channel = Connection(self.server, self.port)
        self.api = self._command_channel.api
        self._command_channel.connect()

        self._event_channel = Connection(self.server, self.port, deduplicate=True)
        self._event_channel.connect()
        self._event_channel.register_for_events(True)

        # FIXME: Figure out exactly how I'm consuming these.
        self._event_queue = queue.Queue()
        self._event_thread = EventThread(self._event_channel, self._event_queue)
        self._event_thread.start()
        #/FIXME

        # TODO: get status

    def close(self) -> None:
        """ Close the connection to our HEOS device

        :return: None
        """
        self._event_thread.stop()
        self._event_thread.join()

        if self._event_channel:
            self._event_channel.close()

        if self._command_channel:
            self._command_channel.close()


    def call(self, group: str, command: str, **kwargs: dict) -> HEOSResult:
        """ Proxy interface to call an API on our Command Channel

        :param group: Group name (e.g. system, player, etc)
        :param command: Command name (e.g. heart_beat_
        :param kwargs: Any parameters that should be sent along with the command
        :return: HEOSResult
        """
        self._check_channel_availability(self._command_channel)

        return self._command_channel.api.call(group, command, **kwargs)

    def subscribe(self, event_name: str, callback: Callable) -> None:
        """ Subscribe a callback function to a specific event

        :param event_name: Event name
        :param callback: Callback function
        :return: None
        """
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
            'event/sources_changed': self._handle_sources_changed,
            'event/players_changed': self._handle_players_changed,
            'event/groups_changed': self._handle_groups_changed,
            'event/player_state_changed': self._handle_player_state_changed,
            'event/player_now_playing_changed': self._handle_now_playing_changed,
            'event/player_now_playing_progress': self._handle_now_playing_progress,
            'event/player_playback_error': self._handle_playback_error,
            'event/player_queue_changed': self._handle_queue_changed,
            'event/player_volume_changed': self._handle_volume_changed,
            'event/repeat_mode_changed': self._handle_repeat_mode_changed,
            'event/shuffle_mode_changed': self._handle_shuffle_mode_changed,
            'event/group_volume_changed': self._handle_group_volume_changed,
            'event/user_changed': self._handle_user_changed,
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


class EventThread(threading.Thread):
    """ Thread that handles receiving events from the event connection """

    def __init__(self, conn: Connection, out_queue: queue.Queue) -> None:
        super().__init__()

        self._connection = conn
        self._out_queue = out_queue
        self.running = False

    def run(self) -> None:
        """ Primary thread function

        :return: None
        """
        self.running = True

        while self.running:
            results = self._connection.api.read_message()
            if results:
                event = HEOSEvent(results)
                print(f"Received event: {event!r}") # FIXME: logging.

                try:
                    self._out_queue.put_nowait(event)
                except queue.Full:
                    pass # throw it away if the queue is full

            time.sleep(0.01)

    def stop(self) -> None:
        """ Signals the thread that it needs to stop

        :return: None
        """
        self.running = False
