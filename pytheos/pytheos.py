#!/usr/bin/env python
""" Provides the primary interface into the library """

from __future__ import annotations

import asyncio
import logging
from typing import Callable, Optional, Union

from . import utils
from . import controllers
from .networking.connection import Connection
from .networking.types import SSDPResponse
from .networking.errors import ChannelUnavailableError
from .models.heos import HEOSEvent
from .models.system import AccountStatus

logger = logging.getLogger('pytheos')


class Pytheos:
    """ Pytheos interface """
    DEFAULT_PORT = 1255

    @staticmethod
    def check_channel_availability(channel: Connection):
        """ Checks to make sure that the provided channel is available.

        :param channel: Channel connection
        :raises: ChannelUnavailableError
        :return: None
        """
        if not channel or not channel.connected:
            raise ChannelUnavailableError()

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

    def __init__(self, server: Union[str, SSDPResponse]=None, port: Optional[int]=DEFAULT_PORT):
        """ Constructor

        :param server: Server hostname or IP
        :param port: Port number
        """
        if isinstance(server, SSDPResponse):
            server = utils.extract_host(server.location)

        self.server: str = server
        self.port: int = port

        self._command_channel = Connection()
        self._event_channel = Connection()
        self._event_queue = asyncio.Queue()
        self._event_task: Optional[asyncio.Task] = None
        self._event_processor: Optional[asyncio.Task] = None
        self._connected: bool = False
        self._event_subscriptions: dict = {}
        self._receive_events: bool = True
        self._account_status: Optional[AccountStatus] = None
        self._account_username: Optional[str] = None
        self._players: list = []
        self._groups: dict = {}     # FIXME?: Not sure I like having this as a dict.
        self._sources: dict = {}    # FIXME?: Not sure I like having this as a dict.

        self.api: Connection = self._command_channel

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

    async def connect(self, enable_event_connection: bool=True, refresh: bool=True) -> Pytheos:
        """ Connect to our HEOS device.

        :param enable_event_connection: Enables establishing an additional connection for system events
        :param refresh: Determines if the system state should be automatically refreshed
        :return: self
        """
        logger.info(f'Connecting to {self.server}:{self.port}')

        await self._command_channel.connect(self.server, self.port)
        self._connected = True

        self._receive_events = enable_event_connection
        if self._receive_events:
            await self._event_channel.connect(self.server, self.port, deduplicate=True)
            await self.enable_event_reception(True)

            loop = asyncio.get_running_loop()
            self._event_task = loop.create_task(self._listen_for_events())
            self._event_processor = loop.create_task(self._process_events())

        if refresh:
            await self.refresh()

        return self

    async def _set_register_for_change_events(self, value: bool):
        """ Notifies HEOS that we want event messages on the event channel.

        :param value: True or False
        :return: None
        """
        await self._event_channel.system.register_for_change_events(value)

    def close(self):
        """ Close the connection to our HEOS device

        :return: None
        """
        logger.info(f'Closing connection to {self.server}:{self.port}')

        if self._event_task:
            self._event_task.cancel()

        if self._event_processor:
            self._event_processor.cancel()

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

    async def refresh(self):
        """ Refreshes internal information from the HEOS system.

        :return: None
        """
        await self.check_account()
        await self.get_players()
        await self.get_groups()
        await self.get_sources()

    async def reboot(self):
        """ Instructs the system to reboot.

        :return: None
        """
        await self.api.system.reboot()

    async def check_account(self) -> tuple:
        """ Checks if the system is logged into HEOS and returns the status and account name, if available.

        :return: tuple
        """
        self._account_status, self._account_username = await self.api.system.check_account()

        return self._account_status, self._account_username

    async def sign_in(self, username: str, password: str):
        """ Signs the system into the HEOS service.

        :param username: Username
        :param password: Password
        :return: None
        """
        await self.api.system.sign_in(username, password)

    async def sign_out(self):
        """ Signs out from the HEOS service.

        :return: None
        """
        await self.api.system.sign_out()

    async def get_players(self):
        """ Retrieves a mapping of IDs to Players present in the HEOS system.

        :return: list
        """
        self._players = [controllers.Player(self, player) for player in await self.api.player.get_players()]

        return self._players

    async def get_group(self, group_id):
        """ Retrieve a specific group by ID.

        :param group_id: Group ID
        :return: PytheosGroup
        """
        groups = await self.get_groups()

        return groups.get(group_id)

    async def get_groups(self):
        """ Retrieves a mapping of IDs to Groups present in the HEOS system.

        :return: dict
        """
        self._groups = {}

        for group in await self.api.group.get_groups():
            self._groups[group.group_id] = controllers.Group(self, group)

        return self._groups

    async def get_sources(self):
        """ Retrieves a mapping of IDs to Sources present in the HEOS system.

        :return:
        """
        self._sources = {}

        for source in await self.api.browse.get_music_sources():
            self._sources[source.source_id] = controllers.Source(self, source)

        return self._sources

    def is_receiving_events(self):
        """ Retrieves whether or not we're receiving events.

        :return: bool
        """
        return self._receive_events

    async def enable_event_reception(self, value):
        """ Enables or disables event reception.

        :param value: True or False
        :return: None
        """
        self._receive_events = value
        await self._set_register_for_change_events(value)

    async def _listen_for_events(self):
        """ Async task that reads messages from the event channel and adds them to our event queue for
        later processing.

        :return: None
        """
        while True:
            results = await self._event_channel.read_message()
            if results:
                event = HEOSEvent(results)
                logger.debug(f"Received event: {event!r}")
                await self._event_queue.put(event)

            await asyncio.sleep(0.5)

    async def _process_events(self):
        """ Async task that processes events that originate from the event channel.

        :return: None
        """
        while True:
            event = await self._event_queue.get()
            if event:
                logger.debug(f'Processing event: {event!r}')
                await self._event_handler(event)

            await asyncio.sleep(0.5)

    async def _event_handler(self, event: HEOSEvent):
        """ Internal event handler

        :param event: HEOS Event
        :return: None
        """
        loop = asyncio.get_running_loop()
        for callback in self._event_subscriptions.get(event.command, []):
            logger.debug(f'Calling registered callback {callback} for event {event!r}')
            loop.create_task(callback(event))

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


async def connect(host: Union[SSDPResponse, str], port: int=Pytheos.DEFAULT_PORT) -> Pytheos:
    """ Connect to the provided host and return a context manager for use with the connection.

    :param host: Host to connect to
    :param port: Port to connect to
    :raises: ValueError
    :return: The Pytheos instance
    """
    if isinstance(host, SSDPResponse):
        host = utils.extract_host(host.location)

    conn = Pytheos(host, port)
    return await conn.connect()
