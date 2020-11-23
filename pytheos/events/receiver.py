#!/usr/bin/env python
from __future__ import annotations

import logging
import queue
import threading
import time

from ..networking import Connection
from .types import HEOSEvent

logger = logging.getLogger(__name__)


class EventReceiverThread(threading.Thread):
    """ Thread that handles receiving events from the event connection """

    def __init__(self, conn: Connection, out_queue: queue.Queue) -> None:
        super().__init__()

        self._connection = conn
        self._out_queue = out_queue
        self._api = conn
        self.running = False

    def run(self) -> None:
        """ Primary thread function

        :return: None
        """
        self.running = True

        while self.running:
            results = self._api.read_message()
            if results:
                event = HEOSEvent(results)
                logger.debug(f"Received event: {event!r}")

                try:
                    self._out_queue.put_nowait(event)
                except queue.Full:
                    pass    # throw it away if the queue is full

            time.sleep(0.01)

    def stop(self) -> None:
        """ Signals the thread that it needs to stop

        :return: None
        """
        self.running = False
