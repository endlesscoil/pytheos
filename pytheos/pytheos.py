#!/usr/bin/env python
import queue
import threading
import time

from . import utils
from .connection import Connection
from .types import HEOSEvent


def connect(host):
    conn = None
    port = None

    if isinstance(host, Pytheos):
        conn = host
    elif isinstance(host, tuple):
        host, port = host
    elif isinstance(host, str) and ':' in host:
        host, port = host.split(':')
        port = int(port)

    if not conn:
        conn = Pytheos(host, port)

    class _wrapper(object):
        def __enter__(self):
            self.conn = conn
            self.conn.connect()

            return self.conn

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.conn:
                self.conn.close()

    return _wrapper()


class Pytheos(object):
    def __init__(self, server=None, port=None, from_response=None):
        if from_response:
            server = utils.extract_host(from_response.location)

        assert server is not None
        assert port is not None

        self.server = server
        self.port = port
        self.api = None

        self._event_subscriptions = {}
        self._init_internal_event_handlers()

    def connect(self):
        self._command_channel = Connection(self.server, self.port)
        self.api = self._command_channel.api
        self._command_channel.connect()

        self._event_channel = Connection(self.server, self.port, deduplicate=True)
        self._event_channel.connect()
        self._event_channel.register_for_events(True)

        self._event_thread = EventThread(self._event_channel, self._event_handler)
        self._event_thread.start()

        # TODO: get status

    def close(self):
        self._event_thread.stop()
        self._event_thread.join()

        if self._event_channel:
            self._event_channel.close()

        if self._command_channel:
            self._command_channel.close()


    def call(self, group, command, **kwargs):
        assert self._command_channel is not None

        header, payload = self._command_channel.api.call(group, command, **kwargs)

        return header, payload

    def subscribe(self, event_name, callback):
        if self._event_subscriptions.get(event_name) is None:
            self._event_subscriptions[event_name] = []

        self._event_subscriptions[event_name].append(callback)

    def _event_handler(self, event):
        subscriptions = self._event_subscriptions.get(event.command, [])
        for callback in subscriptions:
            callback(event)

    def _init_internal_event_handlers(self):
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

    def _handle_sources_changed(self, event):
        raise NotImplementedError()

    def _handle_players_changed(self, event):
        raise NotImplementedError()

    def _handle_groups_changed(self, event):
        raise NotImplementedError()

    def _handle_player_state_changed(self, event):
        raise NotImplementedError()

    def _handle_now_playing_changed(self, event):
        raise NotImplementedError()

    def _handle_now_playing_progress(self, event):
        raise NotImplementedError()

    def _handle_playback_error(self, event):
        raise NotImplementedError()

    def _handle_queue_changed(self, event):
        raise NotImplementedError()

    def _handle_volume_changed(self, event):
        raise NotImplementedError()

    def _handle_repeat_mode_changed(self, event):
        raise NotImplementedError()

    def _handle_shuffle_mode_changed(self, event):
        raise NotImplementedError()

    def _handle_group_volume_changed(self, event):
        raise NotImplementedError()

    def _handle_user_changed(self, event):
        raise NotImplementedError()


class EventThread(threading.Thread):
    def __init__(self, conn, out_queue):
        super().__init__()

        self._connection = conn
        self._out_queue = out_queue
        self.running = False

    def run(self) -> None:
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

    def stop(self):
        self.running = False
